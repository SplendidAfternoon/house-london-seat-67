"""Score and pick the clearest Foreman examples for the demo drill-down."""



from __future__ import annotations



import re

from typing import Any



from classify import is_approved, is_post_permission_admin



MAX_LEN = 280

SWEET_MIN, SWEET_MAX = 50, 220

BALANCED_CATEGORIES = frozenset({"convert", "replace", "extend"})

MIN_EACH_OUTCOME = 2





def _decision_text(decision: str | None) -> str:

    return (decision or "").lower() if isinstance(decision, str) else ""





def is_eligible_candidate(row: dict[str, Any]) -> bool:

    desc = (row.get("description") or "").strip()

    if not desc:

        return False

    decision = _decision_text(row.get("decision"))

    if not decision.strip():

        return False

    if "withdrawn" in decision or "invalid" in decision:

        return False

    if is_post_permission_admin(desc):

        return False

    return True





def example_score(row: dict[str, Any], category: str) -> float:

    desc = (row.get("description") or "").strip()

    text = desc.lower()

    score = 0.0

    approved = is_approved(row.get("decision"))



    n = len(desc)

    if SWEET_MIN <= n <= SWEET_MAX:

        score += 25

    elif n > 320:

        score -= 30



    if category == "convert":

        if approved:

            score += 10

        if any(k in text for k in ("flat", "flats", "c3", "c4", "hmo", "house to", "subdivid", "change of use")):

            score += 40

        if "retrospective" in text:

            score += 10

        if not approved:

            score += 5



    elif category == "replace":

        if approved:

            score += 15

        if re.search(r"demolition of (existing )?(building|buildings|dwelling|house)", text):

            score += 50

        if "redevelopment" in text or "replacement dwelling" in text or "new build" in text:

            score += 35

        if "demolition of existing garage" in text or "demolition of garage" in text:

            score -= 20

        if "demolition of existing rear extension" in text:

            score -= 30

        if not approved:

            score += 5



    elif category == "extend":

        if approved:

            score += 10

        if not approved:

            score += 5

        if any(k in text for k in ("dormer", "rear extension", "loft", "side extension")):

            score += 35

        if "demolition" in text:

            score -= 15



    elif category == "ldc":

        if "lawful development certificate" in text or re.search(r"\bldc\b", text):

            score += 50

        if "loft" in text or "dormer" in text or "extension" in text:

            score += 20



    if row.get("url"):

        score += 5



    return score





def _row_key(row: dict[str, Any]) -> str:

    return (row.get("description") or "")[:120]





def _pack_row(row: dict[str, Any], category: str) -> dict:

    return {

        "description": (row.get("description") or "")[:MAX_LEN],

        "decision": row.get("decision") or "",

        "url": row.get("url") or "",

        "category": category,

    }





def _pick_balanced(

    ranked: list[dict[str, Any]], category: str, limit: int

) -> list[dict]:

    approved_pool = [r for r in ranked if is_approved(r.get("decision"))]

    refused_pool = [r for r in ranked if not is_approved(r.get("decision"))]



    out: list[dict] = []

    seen: set[str] = set()



    def add_from(pool: list[dict[str, Any]], n: int) -> None:

        for row in pool:

            if len(out) >= limit:

                return

            key = _row_key(row)

            if key in seen:

                continue

            seen.add(key)

            out.append(_pack_row(row, category))

            n -= 1

            if n <= 0:

                return



    need_each = min(MIN_EACH_OUTCOME, limit // 2)

    add_from(approved_pool, need_each)

    add_from(refused_pool, need_each)



    for row in ranked:

        if len(out) >= limit:

            break

        key = _row_key(row)

        if key in seen:

            continue

        seen.add(key)

        out.append(_pack_row(row, category))



    return out





def pick_examples(candidates: list[dict[str, Any]], category: str, limit: int = 5) -> list[dict]:

    eligible = [r for r in candidates if is_eligible_candidate(r)]

    ranked = sorted(eligible, key=lambda r: example_score(r, category), reverse=True)



    if category in BALANCED_CATEGORIES and len(ranked) >= limit:

        return _pick_balanced(ranked, category, limit)



    seen: set[str] = set()

    out: list[dict] = []

    for row in ranked:

        key = _row_key(row)

        if key in seen:

            continue

        seen.add(key)

        out.append(_pack_row(row, category))

        if len(out) >= limit:

            break

    return out





def count_outcomes(examples: list[dict]) -> tuple[int, int]:

    approved = sum(1 for e in examples if is_approved(e.get("decision")))

    return approved, len(examples) - approved


