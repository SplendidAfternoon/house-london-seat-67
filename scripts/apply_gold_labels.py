"""Apply gold labels (pass 1 all rows, pass 2 blind subset) to label_sample.csv."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gold_label import gold_classify, gold_classify_b, gold_outcome  # noqa: E402

SAMPLE_PATH = ROOT / "data/processed/label_sample.csv"
PASS2_PATH = ROOT / "data/processed/label_pass2_ids.csv"
SEED = 67
PASS2_N = 20  # per category


def main() -> None:
    if not SAMPLE_PATH.exists():
        sys.exit("Run scripts/export_label_sample.py first")

    df = pd.read_csv(SAMPLE_PATH, dtype=str)
    for idx, row in df.iterrows():
        desc = row.get("description") or ""
        gold = gold_classify(desc)
        pred = row.get("pred_cat") or ""
        outcome = gold_outcome(row.get("decision"))
        note = ""
        if gold != pred:
            note = f"gold!=pred ({gold} vs {pred})"
        if gold == "other":
            note = (note + "; LOW: unclassified").strip("; ")
        df.at[idx, "gold_cat"] = gold
        df.at[idx, "gold_approved"] = outcome
        df.at[idx, "label_notes"] = note

    pass2_ids: list[str] = []
    for cat in sorted(df["pred_cat"].dropna().unique()):
        sub = df[df["pred_cat"] == cat]
        pick = sub.sample(n=min(PASS2_N, len(sub)), random_state=SEED + hash(cat) % 9999)
        pass2_ids.extend(pick["uid"].tolist())

    pass2_set = set(pass2_ids)
    df["pass2_cat"] = ""
    df["pass2_approved"] = ""
    for idx, row in df.iterrows():
        if row["uid"] not in pass2_set:
            continue
        df.at[idx, "pass2_cat"] = gold_classify_b(row.get("description"))
        df.at[idx, "pass2_approved"] = gold_outcome(row.get("decision"))

    df.to_csv(SAMPLE_PATH, index=False)
    pd.DataFrame({"uid": pass2_ids}).to_csv(PASS2_PATH, index=False)
    print(f"    labeled {len(df)} rows in {SAMPLE_PATH}")
    print(f"    pass-2 subset: {len(pass2_ids)} rows")


if __name__ == "__main__":
    main()
