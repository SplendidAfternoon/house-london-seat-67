"""Keyword classifier and outcome coding for Foreman applications."""

from __future__ import annotations

import re
from typing import Literal

from gold_label import gold_classify, gold_outcome

Category = Literal["ldc", "replace", "convert", "extend", "other"]
Outcome = Literal["approved", "refused", "withdrawn", "neutral", "unknown"]

CATEGORY_ORDER = ["extend", "convert", "replace", "ldc"]

CATEGORY_LABELS = {
    "extend": "Extend",
    "convert": "Change of use",
    "replace": "Knock down & rebuild",
    "ldc": "Legalise existing",
    "other": "Other",
}

EXCLUDED_APP_TYPES = frozenset(
    {
        "tree works",
        "tree preservation order",
        "advertisement",
        "advertisement consent",
        "listed building consent",
        "certificate of lawfulness",
    }
)


def classify_description(description: str | None) -> Category:
    return gold_classify(description)  # type: ignore[return-value]


def outcome_bucket(decision: str | None) -> Outcome:
    return gold_outcome(decision)  # type: ignore[return-value]


def is_refused(decision: str | None) -> bool:
    return outcome_bucket(decision) == "refused"


def is_neutral_decision(decision: str | None) -> bool:
    return outcome_bucket(decision) == "neutral"


def is_approved(decision: str | None) -> bool:
    return outcome_bucket(decision) == "approved"


def is_excluded_app_type(app_type: str | None) -> bool:
    if not app_type or not isinstance(app_type, str):
        return False
    return app_type.strip().lower() in EXCLUDED_APP_TYPES


def is_post_permission_admin(description: str | None) -> bool:
    """Re-export for curate_examples and tests."""
    if not description:
        return False
    text = description.lower()
    return bool(
        re.search(
            r"details of condition|discharge of condition|non[- ]material amendment|"
            r"minor material amendment|discharge of schedule|pursuant to planning permission|"
            r"details submitted to satisfy|variation of condition|"
            r"discharge of condition \d+|amendment to planning permission|"
            r"material amendment|details pursuant to|compliance with condition|"
            r"\bs\.?\s*73\b|section 73|discharge of conditions? \d+|"
            r"details of landscaping|details of waste|submission of (a )?details",
            text,
        )
    )


def approval_rate_policy(
    decisions: list[str | None], policy: str = "strict"
) -> tuple[int, int, float]:
    """Return (approved_count, denominator, rate). policy: strict|current|permissive."""
    approved = refused = neutral = unknown = 0
    for d in decisions:
        b = outcome_bucket(d)
        if b == "approved":
            approved += 1
        elif b == "refused":
            refused += 1
        elif b == "neutral":
            neutral += 1
        else:
            unknown += 1

    if policy == "permissive":
        denom = approved + refused + neutral + unknown
        num = approved + neutral
    elif policy == "current":
        denom = approved + refused
        num = approved
    else:  # strict
        denom = approved + refused
        num = approved

    rate = num / denom if denom else 0.0
    return num, denom, rate
