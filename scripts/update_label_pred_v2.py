"""Add pred_cat_v2 after classifier updates (compare to frozen pred_cat)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from classify import classify_description  # noqa: E402

SAMPLE_PATH = ROOT / "data/processed/label_sample.csv"


def main() -> None:
    df = pd.read_csv(SAMPLE_PATH, dtype=str)
    df["pred_cat_v2"] = df["description"].map(classify_description)
    df.to_csv(SAMPLE_PATH, index=False)
    old = (df["pred_cat"] == df["gold_cat"]).mean()
    new = (df["pred_cat_v2"] == df["gold_cat"]).mean()
    print(f"    pred_cat vs gold: {old:.1%}")
    print(f"    pred_cat_v2 vs gold: {new:.1%}")


if __name__ == "__main__":
    main()
