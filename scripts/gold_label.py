"""Gold-standard labeling logic (rubric encoded for validation sample)."""

from __future__ import annotations

import re
from typing import Literal

Outcome = Literal["approved", "refused", "withdrawn", "neutral", "unknown"]
GoldCat = Literal["extend", "convert", "replace", "ldc", "other"]


def _text(description: str | None) -> str:
    return (description or "").lower()


def gold_is_admin(description: str | None) -> bool:
    if not description:
        return False
    text = _text(description)
    return bool(
        re.search(
            r"details of condition|discharge of condition|non[- ]material amendment|"
            r"minor material amendment|discharge of schedule|pursuant to planning permission|"
            r"details submitted to satisfy|variation of condition|"
            r"discharge of condition \d+|amendment to planning permission|"
            r"material amendment|details pursuant to|compliance with condition|"
            r"\bs\.?\s*73\b|section 73|discharge of conditions? \d+|"
            r"details of landscaping|details of waste|details of contamination|"
            r"submission of (a )?details|approval of (the )?details",
            text,
        )
    )


def gold_is_loft_extend(text: str) -> bool:
    if not re.search(r"loft conversion|loft extension|\bdormer\b", text):
        return False
    convert_signals = (
        "flat", "flats", "c3", "c4", "hmo", "subdivid", "change of use",
        "house to", "into flat", "into flats", "to flats",
    )
    return not any(k in text for k in convert_signals)


def gold_is_garage_only_demo(text: str) -> bool:
    if "demolition" not in text and "demolish" not in text:
        return False
    if re.search(r"demolition of (existing )?(garage|conservatory|shed|porch|outbuilding)\b", text):
        if not re.search(r"\b(dwelling|house|houses|block|building|buildings)\b", text):
            return True
    return False


def gold_is_accessory_demo_extend(text: str) -> bool:
    """Demolition of rear extension / dormer then rebuild = extend not replace."""
    if re.search(
        r"demolition of (existing )?(rear extension|side extension|single storey extension|"
        r"rear dormer|existing dormer|lean-to|conservatory)",
        text,
    ):
        if "redevelopment" not in text and "replacement dwelling" not in text:
            return True
    return False


def gold_classify(description: str | None) -> GoldCat:
    if not description or not description.strip():
        return "other"
    text = _text(description)

    if gold_is_admin(description):
        return "other"

    if re.search(r"\blawful development certificate\b|\bldc\b|\blawfulness of", text):
        return "ldc"

    if any(k in text for k in ("replacement dwelling", "replace dwelling", "replacement house")):
        return "replace"

    if gold_is_garage_only_demo(text):
        return "extend"

    if gold_is_accessory_demo_extend(text):
        return "extend"

    if any(k in text for k in ("demolition", "demolish")):
        if re.search(r"\b(redevelopment|replacement|new build|new dwelling|erection of)\b", text):
            return "replace"
        if re.search(r"\b(dwelling|house|houses|flat|flats|block|building|buildings)\b", text):
            return "replace"
        return "extend"

    if gold_is_loft_extend(text):
        return "extend"

    if any(
        k in text
        for k in (
            "conversion", "convert to", "change of use", "subdivision", "sub-divide",
            " into flat", "into flats", "to flats", "flat conversion",
            "house to", "dwellinghouse to", "c3 to", "c4 to", "hmo",
        )
    ):
        return "convert"

    if any(
        k in text
        for k in (
            "extension", "dormer", "rear extension", "side extension", "loft",
            "outbuilding", "two storey", "single storey", "enlargement", "porch",
        )
    ):
        return "extend"

    return "other"


def gold_classify_b(description: str | None) -> GoldCat:
    """Independent pass-2 implementation (same rubric, alternate edge-case order)."""
    if not description or not description.strip():
        return "other"
    text = _text(description)

    if gold_is_admin(description):
        return "other"

    if re.search(r"\blawful development certificate\b|\bldc\b|\bcertificate of lawfulness\b", text):
        return "ldc"

    if gold_is_loft_extend(text):
        return "extend"

    if gold_is_garage_only_demo(text) or gold_is_accessory_demo_extend(text):
        return "extend"

    if any(k in text for k in ("replacement dwelling", "replace dwelling", "replacement house")):
        return "replace"

    if "demolition" in text or "demolish" in text:
        if re.search(r"\b(garage|shed|porch|conservatory)\b", text) and not re.search(
            r"\b(house|dwelling|building|buildings|block)\b", text
        ):
            return "extend"
        return "replace"

    if re.search(
        r"change of use|conversion|convert to|subdivid| into flat|into flats|to flats|"
        r"house to|hmo|c3 to|c4 to|flat conversion",
        text,
    ):
        return "convert"

    if re.search(
        r"extension|dormer|enlargement|outbuilding|single storey|two storey|loft",
        text,
    ):
        return "extend"

    return "other"


def gold_outcome(decision: str | None) -> Outcome:
    if not decision or not isinstance(decision, str) or not decision.strip():
        return "unknown"
    d = decision.lower()
    if any(x in d for x in ("withdrawn", "invalid")):
        return "withdrawn"
    if any(x in d for x in ("refus", "reject", "declin")):
        return "refused"
    if re.search(
        r"prior approval not required|prior approval is not required|"
        r"approval not required|no jurisdiction|no objection|raise no objection|"
        r"^permit$| delegated to ",
        d,
    ):
        return "neutral"
    if any(
        x in d
        for x in (
            "approved", "granted", "grant", "permitted", "permission granted",
            "approve", "lawful", "certificate issued", "certificate granted",
            "not unlawful", "existing lawful",
        )
    ):
        return "approved"
    return "unknown"
