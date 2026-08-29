# External sources — triangulation for Seat 67 claims

Foreman is the **primary** dataset. These sources check direction, not exact percentages, unless we run a row-level join (future work).

## Citation stack

| Layer | Source | Role |
|-------|--------|------|
| Primary | [Foreman](https://foreman.house-london.uk/) | 151k classified applications; mix + borough drill-down |
| Structured planning | [Planning London Datahub (PLD)](https://planningdata.london.gov.uk/) | Official GLA application types, units, commencements — see [`pld-triangulation.md`](pld-triangulation.md) |
| Independent #0 | [The Spike](https://www.house-london.uk/hackathons/zero/solutions/) / [PlanIt](https://www.planit.org.uk/api/) | Convert penalty; text predicts approval better than borough |
| Delivery gap | [House London #0 conclusions](https://www.house-london.uk/hackathons/zero/conclusions/) | Approved vs completed (Homes vs Hotels); small vs large scheme share |
| Policy context | [`policy-context.md`](policy-context.md) | Retrofit-first, demolition history, estate politics |

## Claim → evidence map

### Extend filings dominate; knock-down is ~11%

| Our finding | Foreman | External corroboration |
|-------------|---------|------------------------|
| Extend ~71%, replace ~11% | Keyword taxonomy on descriptions | PLD: **146k** householder permissions vs **8.3k** conservation-area demolition householder apps — **17.5:1** ([`pld-triangulation.md`](pld-triangulation.md)) |
| 6.3:1 extend:replace volume | `validation.json` | #0: small schemes (~15% of **delivered** units); large (100+) 59–72% |

### Extend and knock-down approval rates sit within a few points

| Our finding | Foreman | External corroboration |
|-------------|---------|------------------------|
| Extend 60.2%, replace 57.5% | Wilson CIs, 151k apps | PLD householder permission **82%** vs conservation demolition **84%** ([`pld-triangulation.md`](pld-triangulation.md)) |
| Borough bootstrap CI spans zero | −6.3 to +2.8 pp | Clustered geography; point gap 2.6pp |

### Change-of-use approval runs below extend

| Our finding | Foreman | External corroboration |
|-------------|---------|------------------------|
| Convert ~46% vs extend ~60% | Keyword bucket | **The Spike (PlanIt):** conversion / change-of-use **63.8–65.7% approved** vs London base **~80–85%** ([#0 conclusions](https://www.house-london.uk/hackathons/zero/conclusions/)) |
| Newham convert penalty | Borough drill-down | Text predicts outcome more than borough (Spike ROC-AUC 0.70–0.78) |

**PLD caveat:** Prior-approval “Change of use” rows on PLD are a high-approval subset (~85%) — different population from Foreman’s broad convert bucket. Use Spike/PlanIt for convert penalty, not PLD prior-approval counts alone.

### LDC / legalise ≠ build

| Our finding | Foreman | External corroboration |
|-------------|---------|------------------------|
| LDC ~7% of apps, ~83% approval | Keyword “lawful development” | PLD **Lawful Development Certificate** is a first-class application type ([PLD question set PDF](https://www.london.gov.uk/sites/default/files/planning_london_datahub_questions.pdf)) |
| Barking ~41% LDC | Borough view | Certificates legalise existing use |

### Approved ≠ completed (context only)

Not a Seat 67 headline; background for policy discussion:

- **Homes vs Hotels (#0):** 320,203 approved vs 184,169 completed (2019/20–2023/24) — [conclusions](https://www.house-london.uk/hackathons/zero/conclusions/)
- **Stalled London (#0):** 100k+ approved 2015–21 with no start (PLD-backed; headline likely overestimate per #0 site checks)

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
- Causal explanation for convert penalty or delivery gap
