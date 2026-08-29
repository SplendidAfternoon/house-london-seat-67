"""Export classified applications for R validation."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from classify import classify_description, is_excluded_app_type, outcome_bucket  # noqa: E402

RAW = ROOT / "data/raw/foundations.csv"
OUT = ROOT / "data/processed/classified.csv"


def main() -> None:
    if not RAW.exists():
        sys.exit(f"Missing {RAW}")

    df = pd.read_csv(
        RAW,
        usecols=[
            "reference",
            "description",
            "decision",
            "area_name",
            "app_type",
            "n_dwellings",
            "housing_relevance_score",
            "ward_name",
            "status",
        ],
        dtype=str,
        low_memory=False,
    )
    df = df[~df["app_type"].map(is_excluded_app_type)].copy()
    df["cat"] = df["description"].map(classify_description)
    df["outcome"] = df["decision"].map(outcome_bucket)
    df["approved"] = df["outcome"] == "approved"
    df = df[df["cat"] != "other"].copy()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"    wrote {OUT} ({len(df):,} classified rows)")


if __name__ == "__main__":
    main()
