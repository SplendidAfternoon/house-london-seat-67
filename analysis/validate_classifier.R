#!/usr/bin/env Rscript
# Classifier validation vs gold labels on 400-row stratified sample.

user_lib <- Sys.getenv("R_LIBS_USER")
if (!dir.exists(user_lib)) dir.create(user_lib, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(user_lib, .libPaths()))
for (pkg in c("jsonlite")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, lib = user_lib, repos = "https://cloud.r-project.org", quiet = TRUE)
  }
}
suppressPackageStartupMessages(library(jsonlite))

root <- normalizePath(getwd(), winslash = "/")
sample_path <- file.path(root, "data/processed/label_sample.csv")
out_json <- file.path(root, "data/processed/classifier_validation.json")
out_md <- file.path(root, "reference/classifier-validation.md")

if (!file.exists(sample_path)) stop("Run export_label_sample.py and apply_gold_labels.py first")

df <- read.csv(sample_path, stringsAsFactors = FALSE)
cats <- c("extend", "convert", "replace", "ldc", "other")

if (!"pred_cat_v2" %in% names(df)) {
  df$pred_cat_v2 <- df$pred_cat
}

cohen_kappa <- function(x, y) {
  ok <- !is.na(x) & !is.na(y) & x != "" & y != ""
  x <- x[ok]; y <- y[ok]
  if (length(x) == 0) return(NA)
  tab <- table(factor(x, levels = cats), factor(y, levels = cats))
  n <- sum(tab)
  p0 <- sum(diag(tab)) / n
  pe <- sum(rowSums(tab) * colSums(tab)) / n^2
  if (pe == 1) return(1)
  (p0 - pe) / (1 - pe)
}

prf1 <- function(pred, gold, label) {
  tp <- sum(pred == label & gold == label, na.rm = TRUE)
  fp <- sum(pred == label & gold != label, na.rm = TRUE)
  fn <- sum(pred != label & gold == label, na.rm = TRUE)
  prec <- if (tp + fp > 0) tp / (tp + fp) else 0
  rec <- if (tp + fn > 0) tp / (tp + fn) else 0
  f1 <- if (prec + rec > 0) 2 * prec * rec / (prec + rec) else 0
  list(precision = round(prec, 3), recall = round(rec, 3), f1 = round(f1, 3), support = sum(gold == label, na.rm = TRUE))
}

metrics_for <- function(pred_col) {
  pred <- df[[pred_col]]
  gold <- df$gold_cat
  per_cat <- lapply(setdiff(cats, "other"), function(l) {
    m <- prf1(pred, gold, l)
    c(category = l, unlist(m))
  })
  f1s <- sapply(per_cat, function(x) as.numeric(x["f1"]))
  macro_f1 <- mean(f1s, na.rm = TRUE)
  accuracy <- mean(pred == gold, na.rm = TRUE)
  list(
    accuracy = round(accuracy, 3),
    macro_f1 = round(macro_f1, 3),
    per_category = per_cat
  )
}

pass2 <- df[df$pass2_cat != "", ]
kappa_cat <- cohen_kappa(pass2$gold_cat, pass2$pass2_cat)
kappa_outcome <- mean(pass2$gold_approved == pass2$pass2_approved, na.rm = TRUE)

cm <- as.matrix(table(factor(df$pred_cat_v2, levels = cats), factor(df$gold_cat, levels = cats)))
errors <- df[df$pred_cat_v2 != df$gold_cat, c("pred_cat", "pred_cat_v2", "gold_cat", "description", "label_notes")]

error_taxonomy <- sort(table(paste(df$pred_cat, "->", df$gold_cat)[df$pred_cat != df$gold_cat]), decreasing = TRUE)

payload <- list(
  engine = "R",
  r_version = R.version.string,
  n_sample = nrow(df),
  gold_vs_pred_v1 = metrics_for("pred_cat"),
  gold_vs_pred_v2 = metrics_for("pred_cat_v2"),
  pass2_reliability = list(
    n = nrow(pass2),
    kappa_category = round(kappa_cat, 3),
    outcome_agreement = round(kappa_outcome, 3)
  ),
  confusion_v2 = as.data.frame(cm),
  top_error_patterns = as.list(head(error_taxonomy, 10))
)

write_json(payload, out_json, pretty = TRUE, auto_unbox = TRUE)

md <- c(
  "# Classifier validation (400-app gold sample)",
  "",
  paste0("**Engine:** R ", R.version.string),
  paste0("**Sample n:** ", nrow(df)),
  "",
  "## Gold vs classifier (frozen pred_cat at export)",
  paste0("- Accuracy: **", payload$gold_vs_pred_v1$accuracy * 100, "%**"),
  paste0("- Macro-F1: **", payload$gold_vs_pred_v1$macro_f1, "**"),
  "",
  "## Gold vs classifier (pred_cat_v2 — circular)",
  paste0("- Accuracy: **", payload$gold_vs_pred_v2$accuracy * 100, "%**"),
  paste0("- Macro-F1: **", payload$gold_vs_pred_v2$macro_f1, "**"),
  "",
  "*pred_cat_v2 uses the same rubric as production (`classify.py` → `gold_classify`). Treat as regression check, not independent validation. Use v1 metrics above.*",
  "",
  "## Pass-2 reliability (80-row blind re-label)",
  paste0("- Category Cohen's κ: **", payload$pass2_reliability$kappa_category, "**"),
  paste0("- Outcome agreement: **", payload$pass2_reliability$outcome_agreement * 100, "%**"),
  "",
  "## Top error patterns (pred -> gold, v1)",
  "",
  vapply(names(payload$top_error_patterns), function(k) {
    sprintf("- %s (%s)", k, payload$top_error_patterns[[k]])
  }, character(1)),
  "",
  "Re-run: `python scripts/update_label_pred_v2.py` then `Rscript analysis/validate_classifier.R`",
  ""
)
writeLines(md, out_md, useBytes = TRUE)
cat("Wrote", out_json, "\n")
cat("Macro-F1 v2:", payload$gold_vs_pred_v2$macro_f1, "\n")
