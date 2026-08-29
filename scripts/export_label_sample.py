"""Export stratified 400-row sample for gold labeling (100 per category)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from classify import CATEGORY_ORDER, classify_description, is_excluded_app_type  # noqa: E402

RAW = ROOT / "data" / "raw" / "foundations.csv"
OUT = ROOT / "data/processed/label_sample.csv"
SAMPLE_SIZE = 100
SEED = 67


def stratified_sample(group: pd.DataFrame, n: int) -> pd.DataFrame:
    if len(group) <= n:
        return group
    per_borough = group.groupby("area_name", group_keys=False)
    fractions = per_borough.size() / len(group)
    picks = []
    remaining = n
    areas = list(fractions.index)
    for i, area in enumerate(areas):
        sub = group[group["area_name"] == area]
        if i == len(areas) - 1:
            k = remaining
        else:
            k = max(1, round(n * fractions[area])) if len(sub) >= 1 else 0
            k = min(k, len(sub), remaining)
        if k > 0:
            picks.append(sub.sample(n=k, random_state=SEED + hash(area) % 10000))
            remaining -= k
        if remaining <= 0:
            break
    if not picks:
        return group.sample(n=n, random_state=SEED)
    out = pd.concat(picks, ignore_index=True)
    if len(out) > n:
        out = out.sample(n=n, random_state=SEED)
    elif len(out) < n:
        extra = group.drop(out.index, errors="ignore")
        need = n - len(out)
        if len(extra) >= need:
            out = pd.concat([out, extra.sample(n=need, random_state=SEED + 1)], ignore_index=True)
    return out


def main() -> None:
    if not RAW.exists():
        sys.exit(f"Missing {RAW}")

    df = pd.read_csv(
        RAW,
        usecols=[
            "uid",
            "reference",
            "description",
            "decision",
            "area_name",
            "url",
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
    df["pred_cat"] = df["description"].map(classify_description)
    df = df[df["pred_cat"].isin(CATEGORY_ORDER)].copy()

    parts = []
    for cat in CATEGORY_ORDER:
        sub = df[df["pred_cat"] == cat]
        parts.append(stratified_sample(sub, SAMPLE_SIZE))

    sample = pd.concat(parts, ignore_index=True)
    sample = sample.sample(frac=1, random_state=SEED).reset_index(drop=True)

    for col in ("gold_cat", "gold_approved", "label_notes", "pass2_cat", "pass2_approved"):
        sample[col] = ""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(OUT, index=False)
    print(f"    wrote {OUT} ({len(sample)} rows)")
    for cat in CATEGORY_ORDER:
        print(f"      {cat}: {(sample['pred_cat'] == cat).sum()}")


if __name__ == "__main__":
    main()
