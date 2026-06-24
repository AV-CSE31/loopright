#!/usr/bin/env python3
"""Validate the LoopRight pattern catalog schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_CONTRACT_FIELDS = [
    "objective",
    "state",
    "action",
    "progress",
    "invariant",
    "budget",
    "stop condition",
    "failure condition",
    "recovery",
    "evidence",
]

VALID_CATEGORIES = {
    "agent",
    "concurrency",
    "data",
    "evaluation",
    "ml",
    "reliability",
    "workflow",
}


def require_string(obj: dict, field: str, *, max_length: int = 5000) -> str:
    value = obj.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    value = value.strip()
    if len(value) > max_length:
        raise ValueError(f"{field} must be no longer than {max_length} characters")
    return value


def require_string_list(
    obj: dict,
    field: str,
    *,
    min_items: int = 1,
    max_items: int = 20,
    item_max_length: int = 500,
) -> list[str]:
    value = obj.get(field)
    if not isinstance(value, list) or not (min_items <= len(value) <= max_items):
        raise ValueError(f"{field} must contain between {min_items} and {max_items} items")
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field}[{index}] must be a non-empty string")
        item = item.strip()
        if len(item) > item_max_length:
            raise ValueError(f"{field}[{index}] is too long")
        result.append(item)
    if len(set(result)) != len(result):
        raise ValueError(f"{field} must not contain duplicates")
    return result


def validate_pattern(pattern: dict, slugs: set[str]) -> None:
    if not isinstance(pattern, dict):
        raise ValueError("each pattern must be an object")

    slug = require_string(pattern, "slug", max_length=80)
    pattern_id = require_string(pattern, "id", max_length=20)
    if not pattern_id.startswith("LR-"):
        raise ValueError(f"{slug}.id must start with LR-")
    if slug not in slugs:
        raise ValueError(f"{slug} is not present in slug set")

    for field, max_length in [
        ("title", 120),
        ("category", 40),
        ("summary", 280),
        ("useWhen", 1200),
        ("prompt", 5000),
    ]:
        require_string(pattern, field, max_length=max_length)

    if pattern["category"] not in VALID_CATEGORIES:
        raise ValueError(f"{slug}.category must be one of {sorted(VALID_CATEGORIES)}")

    contract = pattern.get("contract")
    if not isinstance(contract, dict):
        raise ValueError(f"{slug}.contract must be an object")
    for field in REQUIRED_CONTRACT_FIELDS:
        require_string(contract, field, max_length=1200)

    for field in ["redFlags", "tests", "failureModes", "keywords"]:
        require_string_list(pattern, field, min_items=3, max_items=20)

    related = require_string_list(pattern, "relatedPatterns", min_items=1, max_items=8)
    for related_slug in related:
        if related_slug not in slugs:
            raise ValueError(f"{slug}.relatedPatterns references unknown slug {related_slug}")
        if related_slug == slug:
            raise ValueError(f"{slug}.relatedPatterns must not reference itself")

    verification = pattern.get("verification")
    if not isinstance(verification, dict):
        raise ValueError(f"{slug}.verification must be an object")
    require_string(verification, "title", max_length=240)
    require_string(verification, "detail", max_length=1000)


def validate_catalog(catalog: dict) -> None:
    if not isinstance(catalog, dict):
        raise ValueError("catalog must be a JSON object")
    if catalog.get("schemaVersion") != 1:
        raise ValueError("schemaVersion must be 1")
    require_string(catalog, "name", max_length=120)
    require_string(catalog, "description", max_length=500)
    require_string(catalog, "updated", max_length=10)
    if catalog.get("requiredContractFields") != REQUIRED_CONTRACT_FIELDS:
        raise ValueError("requiredContractFields must match LoopRight contract fields")

    patterns = catalog.get("patterns")
    if not isinstance(patterns, list) or len(patterns) < 1:
        raise ValueError("patterns must be a non-empty array")

    slugs = [require_string(pattern, "slug", max_length=80) for pattern in patterns]
    ids = [require_string(pattern, "id", max_length=20) for pattern in patterns]
    if len(set(slugs)) != len(slugs):
        raise ValueError("pattern slugs must be unique")
    if len(set(ids)) != len(ids):
        raise ValueError("pattern ids must be unique")

    slug_set = set(slugs)
    for pattern in patterns:
        validate_pattern(pattern, slug_set)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate-pattern-catalog.py <catalog-json>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
        validate_catalog(catalog)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"invalid pattern catalog: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "patterns": len(catalog["patterns"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

