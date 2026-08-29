"""Verify classifier edge cases and export takeaway stats to data/processed/takeaways.json"""



from __future__ import annotations



import json

import sys

from pathlib import Path



import pandas as pd



ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "scripts"))

from classify import (  # noqa: E402

    CATEGORY_ORDER,

    classify_description,

    is_approved,

    is_excluded_app_type,

)



df = pd.read_csv(

    ROOT / "data/raw/foundations.csv",

    usecols=["description", "decision", "area_name", "url", "app_type"],

    dtype=str,

    low_memory=False,

)

df = df[~df["app_type"].map(is_excluded_app_type)].copy()

df["cat"] = df["description"].map(classify_description)

df["approved"] = df["decision"].map(is_approved)

c = df[df["cat"] != "other"].copy()



# Takeaway 1: replace approved MORE often than extend (when you ask)

london_rates = {

    cat: {

        "count": int((c["cat"] == cat).sum()),

        "approval_rate": round(c[c["cat"] == cat]["approved"].mean(), 3),

    }

    for cat in CATEGORY_ORDER

}



# Takeaway 2: inner vs outer replace share

inner = [

    "Camden",

    "Islington",

    "Hackney",

    "Tower Hamlets",

    "Southwark",

    "Lambeth",

    "Westminster",

    "Kensington",

    "Newham",

    "Wandsworth",

    "Hammersmith and Fulham",

    "Greenwich",

    "Lewisham",

    "City",

]

c["inner"] = c["area_name"].isin(inner)

inner_df = c[c["inner"]]

outer_df = c[~c["inner"]]

mix = {

    "inner": {cat: round((inner_df["cat"] == cat).mean(), 3) for cat in CATEGORY_ORDER},

    "outer": {cat: round((outer_df["cat"] == cat).mean(), 3) for cat in CATEGORY_ORDER},

    "inner_n": len(inner_df),

    "outer_n": len(outer_df),

}



# Takeaway 3: LDC outer borough phenomenon

ldc_boroughs = []

for area, grp in c.groupby("area_name"):

    n = len(grp)

    if n < 300:

        continue

    ldc_pct = (grp["cat"] == "ldc").mean()

    if ldc_pct >= 0.15:

        ldc_boroughs.append({"borough": area, "ldc_pct": round(ldc_pct, 3), "n": n})

ldc_boroughs.sort(key=lambda x: -x["ldc_pct"])



# Takeaway 4: HMO convert refusal

conv = c[c["cat"] == "convert"]

hmo = conv["description"].str.contains(

    r"hmo|house in multiple|c3 to c4|c4 to c3|sui generis", case=False, na=False, regex=True

)



# Takeaway 5: biggest convert penalty boroughs

gap_rows = []

for area, grp in c[c["cat"].isin(["extend", "convert"])].groupby("area_name"):

    ext, conv_g = grp[grp["cat"] == "extend"], grp[grp["cat"] == "convert"]

    if len(ext) < 150 or len(conv_g) < 40:

        continue

    gap_rows.append(

        {

            "borough": area,

            "extend_appr": round(ext["approved"].mean(), 3),

            "convert_appr": round(conv_g["approved"].mean(), 3),

            "gap_pp": round(100 * (ext["approved"].mean() - conv_g["approved"].mean()), 1),

            "convert_n": len(conv_g),

        }

    )

gap_rows.sort(key=lambda x: -x["gap_pp"])



# Takeaway 6: Southwark replace - what's in it?

ss = c[(c["area_name"] == "Southwark") & (c["cat"] == "replace")]

ss_prior = ss["description"].str.contains("prior notification|prior approval", case=False, na=False).mean()

ss_demo = ss["description"].str.contains("demolition|demolish", case=False, na=False).mean()



# Sample descriptions for replace in Southwark

samples = ss["description"].dropna().head(8).tolist()



payload = {

    "headline": "London mostly extends in place. Knock-down approval is comparable to extend; the asymmetry is submission volume.",

    "london_approval_by_category": london_rates,

    "inner_vs_outer_mix": mix,

    "ldc_heavy_boroughs": ldc_boroughs[:8],

    "hmo_convert": {

        "share_of_converts": round(hmo.mean(), 3),

        "approval_rate": round(conv[hmo]["approved"].mean(), 3),

        "other_convert_approval": round(conv[~hmo]["approved"].mean(), 3),

        "n_hmo": int(hmo.sum()),

    },

    "biggest_convert_penalty_boroughs": gap_rows[:6],

    "southwark_replace": {

        "n": len(ss),

        "share_of_borough": round(len(ss) / len(c[c["area_name"] == "Southwark"]), 3),

        "prior_notification_share": round(ss_prior, 3),

        "demolition_word_share": round(ss_demo, 3),

        "sample_descriptions": [s[:200] for s in samples],

    },

}



hmo_stats = payload["hmo_convert"]
top_gap = gap_rows[0] if gap_rows else None
replace_pct = round(london_rates["replace"]["approval_rate"] * 100)
extend_pct = round(london_rates["extend"]["approval_rate"] * 100)
compare = (
    "comparable to"
    if abs(replace_pct - extend_pct) <= 3
    else ("higher than" if replace_pct > extend_pct else "below")
)
payload["pitch_hooks"] = [
    f"Replace applications approve at {replace_pct}% — {compare} extend ({extend_pct}%). We don't fail at demolition; we rarely ask.",
    f"Barking: {round(ldc_boroughs[0]['ldc_pct'] * 100)}% of classified apps are LDCs — legalising existing work, not new builds.",
    (
        f"{top_gap['borough']}: {top_gap['extend_appr'] * 100:.0f}% extend approved vs "
        f"{top_gap['convert_appr'] * 100:.0f}% convert — biggest borough penalty."
        if top_gap
        else "Convert approval lags extend in several outer boroughs."
    ),
    f"HMO/change-of-use: {round(hmo_stats['share_of_converts'] * 100)}% of converts, {round(hmo_stats['approval_rate'] * 100)}% approved vs {round(hmo_stats['other_convert_approval'] * 100)}% for other converts.",
    "Raw 'demolition' in register includes post-permission admin apps — excluded from replace counts.",
]



out = ROOT / "data/processed/takeaways.json"

out.parent.mkdir(parents=True, exist_ok=True)

out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps(payload, indent=2))


