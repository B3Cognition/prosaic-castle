"""Opt-in Python policy for the four byte-pinned shipped Castle productions.

This module never imports SML or the retained SOAR bridge. ``now`` and project
are caller-supplied trusted context. Legacy naive dates retain host-local
timestamp interpretation; use timezone-aware dates for portable replay.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path

from .query_intent import classify_query


POLICY_VERSION = "castle-shipped-v1"
SHIPPED_RULES_SHA256 = "2f733306d6e5464cd2d63a1b639650a9730953b6217469d054fd05ce076821f9"
_RULES = Path(__file__).parent / "rules" / "castle-boost.soar"
_MULTIPLIERS = {
    "recency-boost": 1.25,
    "same-project": 1.15,
    "entity-match": 1.30,
    "type-match": 1.25,
}
_ROOM_TYPES = {
    "decisions": "decision",
    "problems": "problem",
    "preferences": "preference",
    "milestones": "milestone",
    "decision": "decision",
    "problem": "problem",
    "preference": "preference",
    "milestone": "milestone",
    "emotional": "emotional",
}


class UnsupportedRulesError(ValueError):
    """Custom, missing or altered productions require the retained SOAR path."""


def _validate_rules(rules_path):
    path = _RULES if rules_path is None else Path(rules_path)
    try:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise UnsupportedRulesError("custom or unreadable SOAR rules are unsupported") from exc
    if digest != SHIPPED_RULES_SHA256:
        raise UnsupportedRulesError(
            "custom SOAR rules are unsupported; only exact shipped bytes are accepted"
        )


def _age(created_at, now):
    if not isinstance(created_at, str) or not created_at:
        return math.inf
    try:
        value = created_at.replace("Z", "+00:00") if created_at.endswith("Z") else created_at
        return max(0.0, now - datetime.fromisoformat(value).timestamp())
    except (ValueError, TypeError, OverflowError, OSError):
        return math.inf


def _tags(hit, query_type, project, now):
    tags = []
    if _age(hit.get("created_at"), now) < 7 * 24 * 3600:
        tags.append("recency-boost")
    if hit.get("wing", "") == project:
        tags.append("same-project")
    if hit.get("entity_match"):
        tags.append("entity-match")
    if query_type and _ROOM_TYPES.get(hit.get("room") or "") == query_type:
        tags.append("type-match")
    return tags


def apply_shipped_boosts(hits, *, query="", project="default", now, rules_path=None):
    """Return independent annotated copies, preserving incoming order.

    Only the first 50 hits receive tags. If any score is nonpositive and a tag
    fires, all scores (including the tail) use rank-base-v1 before adjustment.
    Legacy audit keys are kept for comparisons; ``boost_policy_version`` and
    ``boost_rules_sha256`` identify the Python policy rather than imply SML ran.
    Callers must supply finite Unix seconds. No clock/project environment is
    consulted. Naive timestamps intentionally preserve legacy host-local time.
    """
    if isinstance(now, bool) or not isinstance(now, (float, int)) or not math.isfinite(now):
        raise ValueError("now must be finite Unix timestamp seconds")
    _validate_rules(rules_path)  # Reject custom rules even for empty hit lists.
    result = deepcopy(list(hits))
    identities = set()
    for hit in result:
        identity = str(
            hit.get("id")
            or f"{hit.get('wing', '')}/{hit.get('room', '')}/{hit.get('source_file', '?')}"
        )
        if identity in identities:
            raise ValueError(
                "duplicate legacy memory identity; unique drawer identities are required"
            )
        identities.add(identity)
    query_type = classify_query(query)
    eligible = result[:50]
    tags = [_tags(hit, query_type, project, now) for hit in eligible]
    if any(hit["score"] <= 0 for hit in result) and any(tags):
        for index, hit in enumerate(result):
            hit.setdefault("raw_relevance_score", hit["score"])
            hit["score"] = (len(result) - index) / len(result)
            hit["adjustment_basis"] = "rank-base-v1"
    for index, hit in enumerate(result):
        hit["boost_policy_version"] = POLICY_VERSION
        hit["boost_rules_sha256"] = SHIPPED_RULES_SHA256
        if index < 50:
            compound = 1.0
            for tag in tags[index]:
                compound *= _MULTIPLIERS[tag]
            compound = max(0.1, min(10.0, compound))
            hit["score_pre_soar"] = hit["score"]
            hit["soar_boost"] = compound
            hit["soar_tags"] = tags[index]
            hit["score"] *= compound
        else:
            # Preserve retained bridge tail audit behavior, including setdefault.
            hit.setdefault("score_pre_soar", hit.get("score", 0.0))
            hit.setdefault("soar_boost", 1.0)
            hit.setdefault("soar_tags", [])
    return result


def apply_shipped_to_reranked(reranked, *, query="", project="default", now, rules_path=None):
    """Pure tuple adapter with legacy filed_at promotion and conditional stable sort."""
    hits = []
    for score, original in reranked:
        row = deepcopy(original)
        row["score"] = score
        if not row.get("created_at"):
            try:
                metadata = json.loads(row.get("metadata_json"))
                row["created_at"] = str(metadata.get("filed_at", ""))
            except (ValueError, TypeError, AttributeError):
                row["created_at"] = ""
        hits.append(row)
    boosted = apply_shipped_boosts(
        hits, query=query, project=project, now=now, rules_path=rules_path
    )
    result = [(hit["score"], hit) for hit in boosted]
    if any(hit.get("soar_boost", 1.0) != 1.0 for hit in boosted):
        result.sort(key=lambda pair: -pair[0])
    return result
