# Classifier validation (400-app gold sample)

**Engine:** R R version 4.6.1 (2026-06-24 ucrt)
**Sample n:** 400

## Gold vs classifier (frozen pred_cat at export)
- Accuracy: **92.2%**
- Macro-F1: **0.923**

## Gold vs classifier (pred_cat_v2 — circular)
- Accuracy: **100%**
- Macro-F1: **1**

*pred_cat_v2 uses the same rubric as production (`classify.py` → `gold_classify`). Treat as regression check, not independent validation. Use v1 metrics above.*

## Pass-2 reliability (80-row blind re-label)
- Category Cohen's κ: **0.883**
- Outcome agreement: **100%**

## Top error patterns (pred -> gold, v1)

- replace -> extend (22)
- extend -> replace (5)
- convert -> extend (3)
- convert -> replace (1)

Re-run: `python scripts/update_label_pred_v2.py` then `Rscript analysis/validate_classifier.R`

