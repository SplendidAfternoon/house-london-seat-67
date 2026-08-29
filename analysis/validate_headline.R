#!/usr/bin/env Rscript
# Headline validation: Wilson CIs, cluster bootstrap, decision policies, strict-replace.

user_lib <- Sys.getenv("R_LIBS_USER")
if (!dir.exists(user_lib)) dir.create(user_lib, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(user_lib, .libPaths()))
if (!requireNamespace("jsonlite", quietly = TRUE)) {
  install.packages("jsonlite", lib = user_lib, repos = "https://cloud.r-project.org", quiet = TRUE)
}
suppressPackageStartupMessages(library(jsonlite))

root <- normalizePath(getwd(), winslash = "/")
classified_path <- file.path(root, "data/processed/classified.csv")
raw_path <- file.path(root, "data/raw/foundations.csv")
out_json <- file.path(root, "data/processed/validation.json")
out_md <- file.path(root, "reference/validation.md")
out_rout <- file.path(root, "reference/validation.Rout")

if (!file.exists(classified_path)) stop("Missing classified.csv — run export_classified.py")

sink(out_rout, split = TRUE)
on.exit(sink(), add = TRUE)
cat("=== Seat 67 validation (R) ===\n", "R version:", R.version.string, "\n\n")

wilson_ci <- function(successes, n, z = 1.96) {
  if (n == 0) return(c(rate = NA, lo = NA, hi = NA))
  p <- successes / n
  denom <- 1 + z^2 / n
  centre <- p + z^2 / (2 * n)
  margin <- z * sqrt((p * (1 - p) + z^2 / (4 * n)) / n)
  c(rate = p, lo = max(0, (centre - margin) / denom), hi = min(1, (centre + margin) / denom))
}

pct <- function(x) sprintf("%.0f%%", round(100 * x))
pct1 <- function(x) sprintf("%.1f%%", round(100 * x, 1))

classify_decision <- function(decision) {
  d <- tolower(trimws(ifelse(is.na(decision), "", decision)))
  if (nchar(d) == 0) return("empty")
  if (grepl("refus|reject|withdrawn|invalid|declin", d)) return("refused")
  if (grepl("prior approval not required|prior approval is not required|approval not required|no objection", d)) {
    return("neutral")
  }
  if (grepl("approved|granted|grant|permitted|permission granted|approve|lawful|certificate", d)) {
    return("approved")
  }
  "unknown"
}

approval_by_policy <- function(outcomes, policy) {
  approved <- sum(outcomes == "approved", na.rm = TRUE)
  refused <- sum(outcomes == "refused", na.rm = TRUE)
  neutral <- sum(outcomes == "neutral", na.rm = TRUE)
  unknown <- sum(outcomes == "unknown", na.rm = TRUE)
  withdrawn <- sum(outcomes == "withdrawn", na.rm = TRUE)
  if (policy == "permissive") {
    num <- approved + neutral
    denom <- approved + refused + neutral + unknown
  } else if (policy == "current") {
    num <- approved
    denom <- approved + refused
  } else {
    num <- approved
    denom <- approved + refused
  }
  rate <- if (denom > 0) num / denom else NA
  c(num = num, denom = denom, rate = rate)
}

cluster_bootstrap_diff <- function(data, cat_a, cat_b, B = 500) {
  agg <- aggregate(
    cbind(approved = data$outcome == "approved", decided = data$outcome %in% c("approved", "refused")) ~ area_name + cat,
    data = data,
    FUN = sum
  )
  agg_a <- agg[agg$cat == cat_a, c("area_name", "approved", "decided")]
  agg_b <- agg[agg$cat == cat_b, c("area_name", "approved", "decided")]
  boroughs <- intersect(agg_a$area_name, agg_b$area_name)
  if (length(boroughs) < 5) return(c(lo = NA, hi = NA, mean = NA))
  diffs <- numeric(B)
  for (i in seq_len(B)) {
    samp <- sample(boroughs, length(boroughs), replace = TRUE)
    ta <- tb <- da <- db <- 0
    for (r in samp) {
      ra <- agg_a[agg_a$area_name == r, ]
      rb <- agg_b[agg_b$area_name == r, ]
      ta <- ta + ra$approved; da <- da + ra$decided
      tb <- tb + rb$approved; db <- db + rb$decided
    }
    pa <- if (da > 0) ta / da else NA
    pb <- if (db > 0) tb / db else NA
    diffs[i] <- (pb - pa) * 100
  }
  q <- quantile(diffs, c(0.025, 0.975))
  c(lo = unname(q[1]), hi = unname(q[2]), mean = mean(diffs))
}

df <- read.csv(classified_path, stringsAsFactors = FALSE)
if (!"outcome" %in% names(df)) {
  raw <- read.csv(raw_path, stringsAsFactors = FALSE)
  df$outcome <- vapply(raw$decision[seq_len(nrow(df))], classify_decision, character(1))
}
df$approved <- df$outcome == "approved"
cats <- c("extend", "convert", "replace", "ldc")

approval_by_cat <- lapply(cats, function(cat) {
  sub <- df[df$cat == cat, , drop = FALSE]
  n <- nrow(sub)
  k <- sum(sub$approved, na.rm = TRUE)
  ci <- wilson_ci(k, n)
  list(category = cat, n = n, approved = k, rate = round(ci["rate"], 3),
       ci_low = round(ci["lo"], 3), ci_high = round(ci["hi"], 3))
})
names(approval_by_cat) <- cats

extend_sub <- df[df$cat == "extend", ]
replace_sub <- df[df$cat == "replace", ]
extend_ci <- wilson_ci(sum(extend_sub$approved), nrow(extend_sub))
replace_ci <- wilson_ci(sum(replace_sub$approved), nrow(replace_sub))

effect_pp <- (replace_ci["rate"] - extend_ci["rate"]) * 100
ext_count <- sum(df$cat == "extend")
rep_count <- sum(df$cat == "replace")
vol_ratio <- ext_count / max(rep_count, 1)

cluster_diff <- cluster_bootstrap_diff(df, "extend", "replace", B = 500)

policy_rows <- lapply(c("strict", "current", "permissive"), function(pol) {
  rows <- lapply(cats, function(cat) {
    sub <- df[df$cat == cat, ]
    ap <- approval_by_policy(sub$outcome, pol)
    list(category = cat, policy = pol, rate = round(ap["rate"], 3))
  })
  rows
})

strict_pat <- "demolition of (existing )?(dwelling|house|houses|building|buildings|block)|redevelopment of (the )?site|replacement dwelling"
df$strict_replace <- grepl(strict_pat, df$description, ignore.case = TRUE)
strict <- df[df$strict_replace, ]
strict_ci <- wilson_ci(sum(strict$approved), nrow(strict))

raw_dec <- read.csv(raw_path, stringsAsFactors = FALSE)[, "decision", drop = FALSE]
raw_dec$bucket <- vapply(raw_dec$decision, classify_decision, character(1))
audit <- as.list(table(raw_dec$bucket))
audit$pct_unknown <- round(100 * audit$unknown / nrow(raw_dec), 2)

interpretation <- sprintf(
  "%.1fpp approval gap (cluster bootstrap 95%% CI %.1f to %.1f). Volume ratio extend:replace %.1f:1 — that is the story.",
  effect_pp, cluster_diff["lo"], cluster_diff["hi"], vol_ratio
)

payload <- list(
  engine = "R",
  r_version = R.version.string,
  generated_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"),
  method = "Wilson CIs + borough cluster bootstrap (B=500)",
  n_classified = nrow(df),
  approval_by_category = approval_by_cat,
  headline_check = list(
    extend_rate = round(extend_ci["rate"], 3),
    replace_rate = round(replace_ci["rate"], 3),
    extend_ci = c(round(extend_ci["lo"], 3), round(extend_ci["hi"], 3)),
    replace_ci = c(round(replace_ci["lo"], 3), round(replace_ci["hi"], 3)),
    effect_size_pp = round(effect_pp, 1),
    volume_ratio_extend_to_replace = round(vol_ratio, 1),
    cluster_bootstrap_diff_pp = list(
      lo = round(cluster_diff["lo"], 1),
      hi = round(cluster_diff["hi"], 1),
      mean = round(cluster_diff["mean"], 1)
    ),
    interpretation = interpretation
  ),
  approval_policy_sensitivity = policy_rows,
  strict_replace = list(
    n = nrow(strict),
    approval_rate = round(strict_ci["rate"], 3),
    ci_low = round(strict_ci["lo"], 3),
    ci_high = round(strict_ci["hi"], 3)
  ),
  decision_audit = list(buckets = audit, pct_unknown = audit$pct_unknown)
)

write_json(payload, out_json, pretty = TRUE, auto_unbox = TRUE)

md <- c(
  "# Validation — R headline check (Seat 67)",
  "",
  paste0("**Engine:** R ", R.version.string),
  paste0("**Generated:** ", payload$generated_at),
  "",
  paste0("**Headline:** ", interpretation),
  "",
  "## Approval by category (Wilson 95% CI)",
  "",
  "| Category | n | Rate | 95% CI |",
  "|----------|---|------|--------|",
  vapply(cats, function(cat) {
    x <- approval_by_cat[[cat]]
    sprintf("| %s | %s | %s | %s–%s |", cat, format(x$n, big.mark = ","),
            pct(x$rate), pct1(x$ci_low), pct1(x$ci_high))
  }, character(1)),
  "",
  "## Cluster bootstrap (replace minus extend approval, pp)",
  "",
  paste0("- Mean diff: **", round(cluster_diff["mean"], 1), "pp**"),
  paste0("- 95% CI: **", round(cluster_diff["lo"], 1), " to ", round(cluster_diff["hi"], 1), " pp**"),
  "",
  "## Decision audit",
  "",
  paste0("- Unknown decision strings: **", audit$pct_unknown, "%**"),
  ""
)
writeLines(md, out_md, useBytes = TRUE)
cat("Wrote", out_json, "\n")
cat(interpretation, "\n")
