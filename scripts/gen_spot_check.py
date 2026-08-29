#!/usr/bin/env python3
"""Generate reference/label-spot-check.md from label sample."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data/processed/label_sample.csv", dtype=str)
pick = df.sample(20, random_state=67)
lines = [
    "# Label spot-check (20 random rows)",
    "",
    "Read descriptions only — flag if gold category looks wrong.",
    "",
]
for _, r in pick.iterrows():
    lines.append(f"## pred {r['pred_cat']} / gold {r['gold_cat']}")
    dec = r.get("decision")
    dec = "" if not isinstance(dec, str) else dec
    desc = r.get("description")
    desc = "" if not isinstance(desc, str) else desc
    lines.append(f"- **Decision:** {dec[:80]}")
    lines.append(f"- **Description:** {desc[:220]}")
    lines.append("")
(ROOT / "reference/label-spot-check.md").write_text("\n".join(lines), encoding="utf-8")
print("    wrote reference/label-spot-check.md")
