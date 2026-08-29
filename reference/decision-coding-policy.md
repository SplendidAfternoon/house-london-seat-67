# Decision coding policy

Used by [`scripts/gold_label.py`](scripts/gold_label.py) → [`scripts/classify.py`](scripts/classify.py) `outcome_bucket()`.

## Rules

| Pattern | Bucket | In approval denominator? |
|---------|--------|--------------------------|
| Approved, Granted, Permitted, Lawful | `approved` | Yes |
| Refused, Rejected, Declined | `refused` | Yes |
| Withdrawn, Invalid | `withdrawn` | No |
| Prior Approval Not Required, No Objection, Permit | `neutral` | Policy-dependent |
| Empty / unrecognised | `unknown` | No |

## Three reporting policies (R sensitivity)

1. **strict** — rate = approved / (approved + refused); neutral and unknown excluded
2. **current** — same as strict (legacy compatibility)
3. **permissive** — rate = (approved + neutral) / (approved + refused + neutral + unknown)

Extend vs replace approval gap stays ~2pp across the three outcome-coding policies. See [`reference/validation.md`](validation.md).

## Top unknown labels (full register)

Mostly GPDO / prior-notification outcomes (~6% of rows). Not treated as grants or refusals unless explicitly approved/refused.
