"""Ad-hoc analysis for less obvious takeaways. Run: python scripts/analyze_takeaways.py"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from classify import CATEGORY_ORDER, classify_description, is_approved  # noqa: E402

df = pd.read_csv(
    ROOT / "data/raw/foundations.csv",
    usecols=[
        "description",
        "decision",
        "area_name",
        "app_type",
        "decided_date",
        "days_to_decision",
        "n_documents",
        "status",
    ],
    dtype=str,
    low_memory=False,
)
df["cat"] = df["description"].map(classify_description)
df["approved"] = df["decision"].map(is_approved)
classified = df[df["cat"] != "other"].copy()

print("=== LONDON MIX ===")
for c in CATEGORY_ORDER:
    sub = classified[classified["cat"] == c]
    pct = 100 * len(sub) / len(classified)
    print(c, len(sub), f"{pct:.1f}%", "appr", round(sub["approved"].mean(), 3))

# extend vs convert approval gap by borough
rows = []
for area, grp in classified[classified["cat"].isin(["extend", "convert"])].groupby("area_name"):
    ext = grp[grp["cat"] == "extend"]
    conv = grp[grp["cat"] == "convert"]
    if len(ext) < 100 or len(conv) < 50:
        continue
    rows.append(
        {
            "area": area,
            "extend_appr": ext["approved"].mean(),
            "convert_appr": conv["approved"].mean(),
            "gap": ext["approved"].mean() - conv["approved"].mean(),
            "n": len(ext) + len(conv),
        }
    )
gaps = pd.DataFrame(rows).sort_values("gap", ascending=False)
print("\n=== BIGGEST extend-minus-convert approval gaps ===")
print(gaps.head(10).to_string(index=False))

# replace share outliers
r = (
    classified.groupby("area_name")
    .apply(
        lambda x: pd.Series(
            {
                "n": len(x),
                "replace_pct": (x["cat"] == "replace").mean(),
                "extend_pct": (x["cat"] == "extend").mean(),
                "ldc_pct": (x["cat"] == "ldc").mean(),
            }
        ),
        include_groups=False,
    )
    .reset_index()
)
r = r[r["n"] >= 500].sort_values("replace_pct", ascending=False)
print("\n=== HIGHEST replace share (n>=500) ===")
print(r.head(10).to_string(index=False))

# LDC hidden stream
print("\n=== LDC share top boroughs ===")
ldc = classified[classified["cat"] == "ldc"]
for area, n in ldc["area_name"].value_counts().head(8).items():
    total = len(classified[classified["area_name"] == area])
    print(area, n, f"({100*n/total:.0f}% of borough classified)")

# Prior notification in replace
rep = classified[classified["cat"] == "replace"]
pn = rep["description"].str.contains("prior notification|prior approval", case=False, na=False)
print(f"\nReplace with prior-notification wording: {pn.sum()}/{len(rep)} ({100*pn.mean():.1f}%)")

# HMO / C3-C4 convert subset
hmo = classified[classified["cat"] == "convert"]
hmo_mask = hmo["description"].str.contains("hmo|c3|c4|house in multiple", case=False, na=False)
print(f"Convert with HMO/C3/C4 wording: {hmo_mask.sum()}/{len(hmo)} ({100*hmo_mask.mean():.1f}%)")
print("HMO-ish convert approval:", round(hmo[hmo_mask]["approved"].mean(), 3))
print("Other convert approval:", round(hmo[~hmo_mask]["approved"].mean(), 3))

# Loft conversion mis-bucketed as convert?
loft_conv = classified["description"].str.contains("loft conversion|roof space", case=False, na=False)
loft_as_convert = classified[loft_conv & (classified["cat"] == "convert")]
loft_as_extend = classified[loft_conv & (classified["cat"] == "extend")]
print(f"\nLoft/roof apps classified convert: {len(loft_as_convert)}, extend: {len(loft_as_extend)}")

# Decision field sanity
print("\n=== Top decision strings (replace) ===")
print(rep["decision"].value_counts().head(8).to_string())
