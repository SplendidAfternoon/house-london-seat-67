#!/usr/bin/env Rscript
# Run full R validation suite.

scripts <- c(
  "analysis/validate_classifier.R",
  "analysis/validate_headline.R",
  "analysis/validate_structured.R"
)
for (s in scripts) {
  cat("\n==", s, "==\n")
  status <- system2("Rscript", s, stdout = "", stderr = "")
  if (status != 0) quit(status = status)
}
cat("\nAll validation scripts complete.\n")
