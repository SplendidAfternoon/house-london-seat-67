"""Classify Foreman applications and write site/data.json."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from classify import (  # noqa: E402
    CATEGORY_LABELS,
    CATEGORY_ORDER,
    classify_description,
    is_approved,
    is_excluded_app_type,
)
from curate_examples import count_outcomes, pick_examples  # noqa: E402

RAW = ROOT / "data" / "raw" / "foundations.csv"
PROCESSED = ROOT / "data" / "processed"
SITE = ROOT / "site"
MAX_EXAMPLES = 5

# Demo boroughs get curated examples; others still get best-available picks.
PRIORITY_BOROUGHS = {
    "Redbridge",
    "Barking and Dagenham",
    "Newham",
    "Kensington",
    "Southwark",
}


def empty_stats() -> dict:
    return {"count": 0, "approved_count": 0}


def pack_category(stats: dict, examples: list[dict], cat: str) -> dict:
    count = stats["count"]
    approved = stats["approved_count"]
    return {
        "count": count,
        "approved_count": approved,
        "approval_rate": round(approved / count, 3) if count else 0.0,
        "examples": examples,
        "label": CATEGORY_LABELS[cat],
    }


def main() -> None:
    if not RAW.exists():
        sys.exit(f"Missing {RAW}. Run scripts/fetch_foreman.py first.")

    df = pd.read_csv(
        RAW, usecols=["description", "decision", "area_name", "url", "app_type"], dtype=str
    )

    london_stats = {cat: empty_stats() for cat in CATEGORY_ORDER}
    borough_stats: dict[str, dict[str, dict]] = defaultdict(
        lambda: {cat: empty_stats() for cat in CATEGORY_ORDER}
    )
    london_candidates: dict[str, list[dict]] = {cat: [] for cat in CATEGORY_ORDER}
    borough_candidates: dict[str, dict[str, list[dict]]] = defaultdict(
        lambda: {cat: [] for cat in CATEGORY_ORDER}
    )
    skipped = 0

    for row in df.itertuples(index=False):
        if is_excluded_app_type(row.app_type if hasattr(row, "app_type") else None):
            skipped += 1
            continue

        cat = classify_description(row.description)
        if cat == "other":
            skipped += 1
            continue

        rec = {
            "description": row.description if isinstance(row.description, str) else "",
            "decision": row.decision if isinstance(row.decision, str) else "",
            "url": row.url if isinstance(row.url, str) else "",
        }
        approved = is_approved(rec["decision"])

        london_stats[cat]["count"] += 1
        if approved:
            london_stats[cat]["approved_count"] += 1
        london_candidates[cat].append(rec)

        area = (row.area_name or "").strip() if isinstance(row.area_name, str) else "Unknown"
        if not area:
            area = "Unknown"
        borough_stats[area][cat]["count"] += 1
        if approved:
            borough_stats[area][cat]["approved_count"] += 1
        borough_candidates[area][cat].append(rec)

    london = {
        cat: pack_category(london_stats[cat], pick_examples(london_candidates[cat], cat), cat)
        for cat in CATEGORY_ORDER
    }

    for cat in ("convert", "replace", "extend"):
        examples = london[cat]["examples"]
        if len(examples) >= 4:
            approved_n, refused_n = count_outcomes(examples)
            print(f"    London {cat}: {approved_n} approved, {refused_n} refused in examples")
            if approved_n == 0 or refused_n == 0:
                sys.exit(
                    f"Example curation failed for London {cat}: "
                    f"need mix of approved and refused (got {approved_n}/{refused_n})"
                )
    boroughs = {}
    for name in sorted(borough_stats):
        boroughs[name] = {
            cat: pack_category(
                borough_stats[name][cat],
                pick_examples(borough_candidates[name][cat], cat),
                cat,
            )
            for cat in CATEGORY_ORDER
        }

    payload = {
        "title": "Extend-in-Place",
        "seat": 67,
        "source": "https://foreman.house-london.uk/",
        "n_applications": int(len(df)),
        "n_classified": int(len(df) - skipped),
        "n_other": skipped,
        "london": london,
        "boroughs": boroughs,
        "honesty": (
            "Sorted from application description text — patterns, not a legal record of each case. "
            "Paperwork-only updates after permission was granted are excluded."
        ),
    }

    takeaways_path = PROCESSED / "takeaways.json"
    if takeaways_path.exists():
        payload["takeaways"] = json.loads(takeaways_path.read_text(encoding="utf-8"))

    PROCESSED.mkdir(parents=True, exist_ok=True)
    SITE.mkdir(parents=True, exist_ok=True)
    out = SITE / "data.json"
    out.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    (PROCESSED / "aggregates.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )

    print(f"    classified {payload['n_classified']:,} / {len(df):,} (other={skipped:,})")
    print(f"    boroughs: {len(boroughs)}")
    for area in ["Redbridge", "Barking and Dagenham"]:
        if area in boroughs:
            ex = boroughs[area]["convert"]["examples"][:2]
            print(f"    sample {area} convert:", ex[0]["description"][:70] if ex else "none")
    print(f"    wrote {out}")


if __name__ == "__main__":
    main()
