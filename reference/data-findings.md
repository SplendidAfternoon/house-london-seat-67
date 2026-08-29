# Data findings — verified takeaways (Seat 67)

Generated after full validation program. See [`reference/methodology-one-pager.md`](reference/methodology-one-pager.md).

## Headline

**London mostly extends in place. Knock-down approval is comparable to extend; the asymmetry is submission volume.**

| Category | Share of classified | Approval rate |
|----------|-------------------|---------------|
| Extend | 71% | 60% |
| Convert | 10% | 46% |
| Replace | 11% | 58% |
| LDC | 7% | 83% |

*151,398 classified of 181,929 total applications.*

## Classifier validation

- 400-app stratified sample (100/category)
- Legacy classifier (frozen pred_cat): macro-F1 **0.92** (main errors: accessory demolition → replace)
- Production classifier now matches gold rubric (pred_cat_v2 = 100% on sample — circular, not independent proof)
- Pass-2 reliability κ: **0.883** (independent `gold_classify_b` on 80 rows)

## LDC stream

| Borough | LDC share |
|---------|-----------|
| Barking and Dagenham | 41% |
| Waltham Forest | 35% |
| Newham | 25% |

## Convert penalty (borough)

| Borough | Extend ok | Convert ok | Gap |
|---------|-----------|------------|-----|
| Newham | 66% | 26% | 40pp |
| Haringey | 87% | 54% | 32pp |
| Lambeth | 72% | 39% | 32pp |

## HMO converts

~28% of convert apps; HMO approval ~40% vs other converts ~48%.

## Reproduce

```powershell
python scripts/export_classified.py
python scripts/export_label_sample.py
python scripts/apply_gold_labels.py
Rscript analysis/run_validation.R
python run.py
```
