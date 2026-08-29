# Labeling rubric — Seat 67 gold standard

Agent-applied rubric encoded in [`scripts/gold_label.py`](scripts/gold_label.py). Production classifier delegates to the same logic via [`scripts/classify.py`](scripts/classify.py).

## Categories

| Category | Label when | Not when |
|----------|------------|----------|
| **extend** | Enlargement of existing dwelling: extensions, dormers, lofts without flat split | Whole-building demolition; pure change-of-use |
| **convert** | Change of use, subdivision to flats, HMO, C3/C4 | Loft-only dormer; admin paperwork |
| **replace** | Demolition/redevelopment of dwelling or main building | Garage/conservatory-only demo; demo of existing extension then rebuild |
| **ldc** | Lawful Development Certificate / lawfulness proof | Full planning permission for new work |
| **other** | Condition discharge, s.73, amendment, unclassifiable | — |

## Outcomes (`gold_approved`)

| Value | When |
|-------|------|
| `approved` | Granted, approved, lawful certificate issued |
| `refused` | Refused, rejected, declined |
| `withdrawn` | Withdrawn, invalid |
| `neutral` | Prior approval not required, no objection, permit-only workflow |
| `unknown` | Empty or unrecognised decision string |

## Worked examples (from sample)

### extend
- "Single storey rear extension following demolition of existing conservatory" → **extend** (accessory demo + extension)
- "Rear dormer extension to facilitate loft conversion" → **extend** (no flat split)

### convert
- "Change of use from dwelling (C3) to HMO (C4)" → **convert**
- "Subdivision of house into two flats" → **convert**

### replace
- "Demolition of existing building and erection of new dwelling" → **replace**
- "Redevelopment of site including demolition of existing block" → **replace**

### ldc
- "Application for a Lawful Development Certificate for a rear dormer" → **ldc**

## Reliability

- **Pass 1:** all 400 stratified rows labeled
- **Pass 2:** 80 rows (20/category) blind re-label with same rubric
- **Target κ:** ≥ 0.75 category agreement (pass-1 vs pass-2)

See [`reference/classifier-validation.md`](reference/classifier-validation.md) for metrics.
