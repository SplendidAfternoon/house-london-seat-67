# Seat 67 — The Replacement Gap

House London hackathon #1 interactive explorer: **why aren't we tearing down old buildings?** The Foreman application stream says we mostly **extend** Victorian stock in place — demolition/replacement is a thin tail, and **conversions are refused more often** than extensions.

> *Everyone asks if we should tear down. I asked if the system ever does. The applications say: we dormer.*

## Run

```powershell
cd C:\Users\katak\Projects\house-london-seat-67
python run.py
```

First run downloads Foreman applications (cached in `data/raw/`). Then opens http://localhost:8099.

**Offline demo:** `dist/replacement-gap.html` (double-click, no wifi).

**Slides:** `dist/presentation.html` (methodology deck for judges).

**Repo:** https://github.com/SplendidAfternoon/house-london-seat-67

## Honesty

- Keyword classifier on `description` text — illustrative, not ground truth.
- Descriptive analysis of application mix — not planning advice either way.
- Data: [Foreman](https://foreman.house-london.uk/)
- **Validation (R):** Full program — `reference/methodology-one-pager.md`
  ```powershell
  python scripts/export_classified.py
  python scripts/export_label_sample.py
  python scripts/apply_gold_labels.py
  python scripts/update_label_pred_v2.py
  Rscript analysis/run_validation.R
  ```

Team: **Seat 67 / The Replacement Gap**
