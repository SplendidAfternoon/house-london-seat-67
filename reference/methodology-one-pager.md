# Methodology one-pager — Seat 67

## What we built

Interactive explorer of **151,398** classified Foreman planning applications across London, bucketed by keyword taxonomy: **extend / convert / replace / LDC**.

**Offline demo:** `dist/tear-down-applications.html`

## How we validated

| Layer | Method | Result |
|-------|--------|--------|
| **Taxonomy** | 400-app stratified sample, agent gold rubric + independent pass-2 (`gold_classify_b`) | Legacy classifier **92.2%** acc / macro-F1 **0.92**; pass-2 κ on 80 rows — see classifier-validation.md |
| **Approval rates** | Wilson 95% CIs on 151k apps | Extend 60.2% (59.9–60.4); replace 57.5% (56.8–58.3) |
| **Headline** | Effect size + volume ratio | **−2.6pp** approval gap; **6.3:1** extend:replace volume |
| **Cluster uncertainty** | Borough bootstrap (B=500) | Replace−extend diff 95% CI: −6.3 to +2.8 pp |
| **Outcome coding** | 3-policy sensitivity | Gap stable under strict/current/permissive |
| **Structured fields** | n_dwellings, housing_relevance_score cross-check | Mostly empty / non-discriminating — see `reference/structured-validation.md` |
| **External triangulation** | PLD guest API counts + House London #0 conclusions | See `reference/external-sources.md`, `reference/pld-triangulation.md` |

## Summary

> 71% extend, 11% knock-down & rebuild. Stated approval: extend 60%, knock-down 58%. Count ratio ~6:1.

## What we do not claim

- Not ground-truth planning policy analysis
- Not independent human-labeled gold standard (agent rubric with two-pass reliability)
- Not pro-demolition
- Borough penalty rankings are exploratory (no multiple-comparison adjustment)

## Reproduce

```powershell
python scripts/export_classified.py
python scripts/export_label_sample.py
python scripts/apply_gold_labels.py
python scripts/update_label_pred_v2.py
Rscript analysis/run_validation.R
python scripts/sample_pld.py
python scripts/build_site.py
python scripts/build_standalone.py
```

## Key references

- [`reference/external-sources.md`](reference/external-sources.md) — claim → evidence map
- [`reference/pld-triangulation.md`](reference/pld-triangulation.md) — GLA structured type counts
- [`reference/classifier-validation.md`](reference/classifier-validation.md)
- [`reference/validation.md`](reference/validation.md)
- [`reference/labeling-rubric.md`](reference/labeling-rubric.md)
- [`reference/decision-coding-policy.md`](reference/decision-coding-policy.md)
