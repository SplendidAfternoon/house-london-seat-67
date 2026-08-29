#!/usr/bin/env Rscript
# Structured-field cross-checks vs classifier categories.

user_lib <- Sys.getenv("R_LIBS_USER")
if (!dir.exists(user_lib)) dir.create(user_lib, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(user_lib, .libPaths()))
if (!requireNamespace("jsonlite", quietly = TRUE)) {
  install.packages("jsonlite", lib = user_lib, repos = "https://cloud.r-project.org", quiet = TRUE)
}
suppressPackageStartupMessages(library(jsonlite))

root <- normalizePath(getwd(), winslash = "/")
classified_path <- file.path(root, "data/processed/classified.csv")
out_json <- file.path(root, "data/processed/structured_validation.json")
out_md <- file.path(root, "reference/structured-validation.md")

df <- read.csv(classified_path, stringsAsFactors = FALSE)
df$n_dwellings_num <- suppressWarnings(as.numeric(df$n_dwellings))
df$hrs_num <- suppressWarnings(as.numeric(df$housing_relevance_score))

cats <- c("extend", "convert", "replace", "ldc")

dwell_by_cat <- tapply(df$n_dwellings_num, df$cat, function(x) {
  x <- x[!is.na(x)]
  c(median = median(x, na.rm = TRUE), pct_gt0 = mean(x > 0, na.rm = TRUE))
}, simplify = FALSE)

hrs_by_cat <- tapply(df$hrs_num, df$cat, function(x) {
  x <- x[!is.na(x)]
  c(median = median(x, na.rm = TRUE), mean = mean(x, na.rm = TRUE))
}, simplify = FALSE)

app_type_tab <- as.data.frame.matrix(table(df$cat, df$app_type))

ldc_app_types <- sort(table(df$app_type[df$cat == "ldc"]), decreasing = TRUE)
dwell_summary <- lapply(cats, function(cat) {
  x <- df$n_dwellings_num[df$cat == cat]
  non_null <- sum(!is.na(x))
  gt0 <- sum(x > 0, na.rm = TRUE)
  c(non_null = non_null, gt0 = gt0, pct_gt0_of_non_null = if (non_null > 0) gt0 / non_null else NA)
})
names(dwell_summary) <- cats

payload <- list(
  engine = "R",
  n = nrow(df),
  n_dwellings_field = dwell_summary,
  housing_relevance_median = lapply(hrs_by_cat, function(x) round(unlist(x), 3)),
  top_app_types_for_ldc = as.list(head(ldc_app_types, 10)),
  app_type_by_category_rows = nrow(app_type_tab)
)

write_json(payload, out_json, pretty = TRUE, auto_unbox = TRUE)

md <- c(
  "# Structured-field validation",
  "",
  paste0("Classified n: **", nrow(df), "**"),
  "",
  "## n_dwellings field (mostly empty in Foreman)",
  "",
  "*Percentages are of rows with a non-null value, not of all classified apps.*",
  "",
  vapply(cats, function(cat) {
    s <- dwell_summary[[cat]]
    sprintf(
      "- %s: **%s** non-null; **%s** > 0 (%.0f%% of non-null)",
      cat, format(as.integer(s["non_null"]), big.mark = ","),
      format(as.integer(s["gt0"]), big.mark = ","),
      100 * as.numeric(s["pct_gt0_of_non_null"])
    )
  }, character(1)),
  "",
  "## Housing relevance score (median by category)",
  "",
  vapply(cats, function(c) {
    m <- payload$housing_relevance_median[[c]]["median"]
    sprintf("- %s: %s", c, m)
  }, character(1)),
  "",
  "See `data/processed/structured_validation.json` for full tables.",
  ""
)
writeLines(md, out_md, useBytes = TRUE)
cat("Wrote", out_json, "\n")
