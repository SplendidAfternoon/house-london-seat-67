# External sources — triangulation for Seat 67 claims

Foreman is our **primary** dataset. These sources **corroborate direction**, not exact percentages, unless we run a row-level join (future work).

## Citation stack (one slide)

| Layer | Source | Role |
|-------|--------|------|
| Primary | [Foreman](https://foreman.house-london.uk/) | 151k classified applications; mix + borough drill-down |
| Structured planning | [Planning London Datahub (PLD)](https://planningdata.london.gov.uk/) | Official GLA application types, units, commencements — see [`pld-triangulation.md`](pld-triangulation.md) |
| Independent #0 | [The Spike](https://www.house-london.uk/hackathons/zero/solutions/) / [PlanIt](https://www.planit.org.uk/api/) | Convert penalty; text predicts approval better than borough |
| Delivery gap | [House London #0 conclusions](https://www.house-london.uk/hackathons/zero/conclusions/) | Approved vs completed (Homes vs Hotels); small vs large scheme share |
| Policy context | [`policy-context.md`](policy-context.md) | Retrofit-first, demolition history, estate politics |

## Claim → evidence map

### “We extend in place — replace is rare (volume gap)”

| Our finding | Foreman | External corroboration |
|-------------|---------|------------------------|
| Extend ~71%, replace ~11% | Keyword taxonomy on descriptions | PLD: **146k** householder permissions vs **8.3k** conservation-area demolition householder apps — **17.5:1** ([`pld-triangulation.md`](pld-triangulation.md)) |
| 6.3:1 extend:replace volume | `validation.json` | #0: small schemes (~15% of **delivered** units); large (100+) 59–72% — replacement-scale work is structurally rarer at application level |

**Safe to say:** “London mostly submits extend-in-place applications; estate-scale replace is a thin tail — consistent with GLA structured types and #0 delivery mix.”

### “Replace and extend approval rates are similar (~58–60%)”

| Our finding | Foreman | External corroboration |
|-------------|---------|------------------------|
| Extend 60.2%, replace 57.5% | Wilson CIs, 151k apps | PLD householder permission **82%** vs conservation demolition **84%** — comparable ([`pld-triangulation.md`](pld-triangulation.md)) |
| Cluster bootstrap CI spans zero | Borough bootstrap −6.3 to +2.8 pp | Not a “refusal gap” story once geography is clustered |

**Safe to say:** “Approval rates are comparable; the replacement gap is **what we ask for**, not systematic refusal of demolition.”

### “Convert / change-of-use is harder than extend”

| Our finding | Foreman | External corroboration |
|-------------|---------|------------------------|
| Convert ~46% vs extend ~60% | Keyword bucket | **The Spike (PlanIt):** conversion / change-of-use **63.8–65.7% approved** vs London base **~80–85%** ([#0 conclusions](https://www.house-london.uk/hackathons/zero/conclusions/)) |
| Newham convert penalty | Borough drill-down | Same structural pattern: **what you propose** predicts outcome more than **where** (Spike ROC-AUC 0.70–0.78 text-only) |

**PLD caveat:** Prior-approval “Change of use” rows on PLD are a high-approval subset (~85%) — different population from Foreman’s broad convert bucket. Use Spike/PlanIt for convert penalty, not PLD prior-approval counts alone.

**Safe to say:** “Convert penalty matches independent PlanIt analysis from House London #0 — not a Foreman-only artefact.”

### “LDC / legalise ≠ build”

| Our finding | Foreman | External corroboration |
|-------------|---------|------------------------|
| LDC ~7% of apps, ~83% approval | Keyword “lawful development” | PLD **Lawful Development Certificate** is a first-class application type ([PLD question set PDF](https://www.london.gov.uk/sites/default/files/planning_london_datahub_questions.pdf)) |
| Barking ~41% LDC | Borough view | Certificates legalise existing use — structurally non-build in both datasets |

### “Approved ≠ completed (post-permission gap)”

Not our headline, but strengthens policy urgency without claiming causation:

- **Homes vs Hotels (#0):** 320,203 approved vs 184,169 completed (2019/20–2023/24) — [conclusions](https://www.house-london.uk/hackathons/zero/conclusions/)
- **Stalled London (#0):** 100k+ approved 2015–21 with no start (PLD-backed; headline likely overestimate per #0 site checks)

**Safe to say:** “We rarely **ask** to replace; London also **under-delivers** much of what it approves — different mechanisms.”

## House London Drive (not yet joined)

From the [intro doc](https://docs.google.com/document/d/1u7gQN30yHh79ubEZU5cYSfAED5NyUMnU0dYvdIeEyZQ/export?format=txt):

| Drive asset | Use for Seat 67 |
|-------------|-----------------|
| **Data Asset Register** | Curated index — pick Planning Permission rows with API links |
| **#0 GitHub / solutions** | Spike, Homes vs Hotels code patterns |
| **WhereToBuild (Warwick)** | Demand/supply pressure — **DUA: do not publish raw online before contact** |

## Reproduce external checks

```powershell
python scripts/sample_pld.py
```

Outputs: `data/processed/pld_sample.json`, `reference/pld-triangulation.md`.

## What we still do not claim

- Row-level Foreman ↔ PLD join (Foreman `reference` field ~99% empty)
- Exact PLD percentages match Foreman percentages (different population and indexing)
- Causal “why” for convert penalty or delivery gap
