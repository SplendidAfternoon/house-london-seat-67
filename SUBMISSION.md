# Submission — Seat 67: Tear-Down Applications

| Field | Value |
|-------|--------|
| **Seat** | 67 |
| **Question** | Why aren't we tearing down old buildings? |
| **Team** | Seat 67 / Tear-Down Applications |

## Demo

**GitHub Pages:**

- https://splendidafternoon.github.io/presentation.html
- https://splendidafternoon.github.io/tear-down-applications.html

**Offline:** `dist/tear-down-applications.html` or `dist/presentation.html` — double-click. Arrow keys on slides.

## Methodology

151k Foreman applications classified by keyword taxonomy (extend / convert / replace / LDC). Validated on a **400-app stratified gold sample** (agent rubric, pass-2 κ=0.88, legacy classifier macro-F1 0.92 — not independent human audit). Approval rates use **R Wilson 95% CIs**. Extend : knock-down count ratio **6.3 : 1**; stated approval **60% vs 58%** (~2.6pp gap, borough bootstrap CI spans zero). Details: `reference/methodology-one-pager.md`.

## Run from source

```powershell
cd C:\Users\katak\Projects\house-london-seat-67
python run.py
```

## What it shows

Borough bar chart of application mix; click a segment for curated examples (balanced approved/refused for convert/replace).

## Judging form

https://forms.gle/c14LXvLtcESi6Lgz8

## Checklist

- [ ] Pages URLs open on presenting machine
- [ ] Offline HTML opens in airplane mode (backup)
- [ ] Under 3:00 if timed

## Limits (one line)

Keyword classifier on 400 stratified applications; description-based buckets, not council form codes.

Policy bibliography: `reference/policy-context.md`
