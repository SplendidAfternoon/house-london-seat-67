# Seat 67 — Tear-Down Applications (Technical Reference)

**Present**

| | Link |
|---|------|
| **Presentation** | https://splendidafternoon.github.io/house-london-seat-67/presentation.html |
| **Interactive map** | https://splendidafternoon.github.io/house-london-seat-67/tear-down-applications.html |

Slides: ← → arrow keys. Map: pick a borough, click a bar segment.

> Foreman keyword sort of 151,398 London planning applications, grouped by description into extend, change of use, knock-down & rebuild, and legalise existing.

House London #1 hackathon artifact. Categories come from free-text descriptions, not council form codes. Post-permission admin (condition discharges, S73) excluded. Counts applications and stated decisions, not homes built.

## Findings

| Measure | London-wide | Method |
|---------|-------------|--------|
| Mix | ~71% extend · ~11% knock-down & rebuild · ~10% change of use · ~7% legalise | Keyword buckets |
| Extend : knock-down count | 6.3 : 1 | n=151,398 classified |
| Extend approval | 60.2% | Wilson 95% CI |
| Knock-down approval | 57.5% | Wilson 95% CI |
| Extend − knock-down gap | 2.6pp (borough bootstrap 95% CI −6.3 to +2.8pp) | `analysis/validate_headline.R` |
| Change-of-use approval | 45.6% | Same classifier |
| GLA cross-check | 17.5 : 1 householder permission vs conservation demolition | `scripts/sample_pld.py` |

Extend applications outnumber knock-down filings ~6:1. Stated approval rates for the two sit within a few percentage points.

## System Architecture

### 1. Ingest
- **Foreman CSV:** ~182k applications; cached under `data/raw/` (gitignored). Fetch: `scripts/fetch_foreman.py`.

### 2. Classification
- **Buckets:** `scripts/classify.py`, `scripts/gold_label.py`.
- **Gold sample:** 400 stratified rows; legacy classifier macro-F1 0.92; pass-2 κ 0.883 on 80 rows.

### 3. Aggregation & UI
- **Borough cuts + examples:** `scripts/build_site.py` → `site/data.json`.
- **Offline bundle:** `scripts/build_standalone.py` → `dist/tear-down-applications.html`.
- **GitHub Pages:** `scripts/publish_pages.py` → `docs/`.

### 4. Validation
- **R:** Wilson CIs, borough bootstrap, decision-policy sensitivity (`analysis/run_validation.R`).
- **PLD:** guest API phrase counts (`scripts/sample_pld.py`).

## Artifacts

| File | Role |
|------|------|
| [presentation.html](https://splendidafternoon.github.io/house-london-seat-67/presentation.html) | Slide deck (GitHub Pages) |
| [tear-down-applications.html](https://splendidafternoon.github.io/house-london-seat-67/tear-down-applications.html) | Borough bar chart + examples (GitHub Pages) |
| `dist/tear-down-applications.html` | Same map, offline |
| `dist/presentation.html` | Same slides, offline |
| `reference/methodology-one-pager.md` | Validation map |
| `reference/validation.md` | R output |

## Run

```powershell
cd C:\Users\katak\Projects\house-london-seat-67
python run.py
```

First run downloads Foreman (~115 MB). Serves http://localhost:8099.

```powershell
python scripts/export_classified.py
python scripts/export_label_sample.py
python scripts/apply_gold_labels.py
python scripts/update_label_pred_v2.py
Rscript analysis/run_validation.R
python scripts/sample_pld.py
```

**Repo:** https://github.com/SplendidAfternoon/house-london-seat-67
