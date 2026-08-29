# PLD triangulation sample

**Fetched:** 2026-08-29T14:42:23Z (UTC)  
**Source:** [Planning London Datahub](https://planningdata.london.gov.uk/) guest API  
**Method:** Exact-phrase count queries (`match_phrase`) — fuzzy `match` over-counts on `application_type_full`.

Directional cross-check of Foreman keyword buckets against GLA structured fields. Not a row-level join.

## Coarse application_type (index counts)

| PLD type | Count |
|----------|------:|
| Householder | 210,019 |
| All Other | 1,003,669 |
| Prior Approval | 66,219 |

## Structured types vs Foreman buckets

| PLD application_type_full | Count | Approval (decided) | Foreman bucket |
|---------------------------|------:|-------------------:|----------------|
| Householder planning permission | 146,086 | 81.9% (108,954/133,040) | extend |
| Householder + demolition (conservation) | 8,344 | 84.2% (6,276/7,455) | replace |
| Lawful development: Proposed use | 70,630 | 83.3% (48,515/58,226) | ldc |
| Prior approval: Change of use (prefix) | 8,033 | 85.2% (6,245/7,326) | convert (subset) |
| Full planning permission | 240,916 | — | mixed |

**Volume ratio (extend:replace on PLD structured types): 17.5:1** — Foreman keyword ratio 6.3:1; same direction, PLD gap wider.

**Approval on PLD householder extend vs conservation demolition: 81.9% vs 84.2%** — comparable, matches Foreman ~60% vs ~58% story.

## Sample bucket mix (5k docs, type_full → buckets)

| Bucket | Share |
|--------|------:|
| admin | 8.9% |
| convert | 0.4% |
| extend | 22.2% |
| ldc | 6.6% |
| mixed | 11.6% |
| other | 49.6% |
| replace | 0.9% |

## How to use in the pitch

- **Volume gap (strong):** PLD counts **146,086** householder permissions vs **8,344** householder demolition-in-conservation — **17.5:1**. Same story as Foreman six-to-one extend:replace.
- **Approval similarity (strong):** Structured householder extend and demolition types approve at similar rates on PLD — gap is volume, not refusal.
- **Convert penalty (use #0, not this PLD slice):** Prior-approval office-to-resi change-of-use is a high-approval subset. For convert penalty cite [The Spike / PlanIt](https://www.house-london.uk/hackathons/zero/conclusions/) — conversion 63.8–65.7% vs ~80–85% base — and Foreman keyword convert bucket (46%).

Full JSON: `data/processed/pld_sample.json`  
Claim map: [`external-sources.md`](external-sources.md)

Re-run: `python scripts/sample_pld.py`
