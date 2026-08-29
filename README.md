# Seat 67 — Extend-in-Place (Technical Reference)

> A keyword-sorted audit of 151,398 London planning applications (Foreman) asking whether demolition-and-rebuild is refused more often than extension — or simply submitted less often.

**Note:** House London #1 hackathon artifact. Categories are inferred from free-text descriptions, not council form codes. Post-permission admin (condition discharges, S73) is excluded. This measures application mix and stated decisions, not homes built.

## Findings

| Claim | London-wide | Method |
|-------|-------------|--------|
| Submission mix | ~71% extend · ~11% knock-down & rebuild · ~10% change of use · ~7% legalise | Keyword buckets on Foreman descriptions |
| Volume ratio | 6.3 : 1 extend vs knock-down | Counts on classified n=151,398 |
| Approval (extend vs knock-down) | 60.2% vs 57.5% | Wilson 95% CI; borough cluster bootstrap CI spans zero |
| Change-of-use penalty | 45.6% vs 60.2% extend | Same classifier; direction matches House London #0 / PlanIt |
| External check | 17.5 : 1 householder permission vs conservation demolition (GLA Datahub) | `scripts/sample_pld.py` phrase counts |

Headline: **the asymmetry is in what gets filed, not in refusal conditional on filing.**

## System Architecture

### 1. Ingest
- **Foreman CSV:** ~182k applications; cached under `data/raw/` (gitignored, re-fetch via `scripts/fetch_foreman.py`).

### 2. Classification
- **Four buckets:** extend · change of use · knock-down & rebuild · legalise existing (`scripts/classify.py`, `scripts/gold_label.py`).
- **Gold sample:** 400 stratified rows; legacy classifier macro-F1 0.92; pass-2 κ 0.883 on 80 rows.

### 3. Aggregation & UI
- **Borough cuts + curated examples:** `scripts/build_site.py` → `site/data.json`.
- **Offline bundle:** `scripts/build_standalone.py` → `dist/replacement-gap.html`.

### 4. Validation
- **R:** Wilson CIs, borough bootstrap, decision-policy sensitivity (`analysis/run_validation.R`).
- **PLD triangulation:** guest API counts (`scripts/sample_pld.py`).

## Artifacts

| File | Role |
|------|------|
| `dist/replacement-gap.html` | Interactive explorer (offline) |
| `dist/presentation.html` | Slide deck for the room |
| `reference/methodology-one-pager.md` | Validation map |
| `reference/validation.md` | R headline output |

## Run

```powershell
cd C:\Users\katak\Projects\house-london-seat-67
python run.py
```

First run downloads Foreman (~115 MB). Serves http://localhost:8099.

Full validation chain:

```powershell
python scripts/export_classified.py
python scripts/export_label_sample.py
python scripts/apply_gold_labels.py
python scripts/update_label_pred_v2.py
Rscript analysis/run_validation.R
python scripts/sample_pld.py
```

**Repo:** https://github.com/SplendidAfternoon/house-london-seat-67
