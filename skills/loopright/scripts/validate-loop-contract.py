#!/usr/bin/env python3
"""Lightweight LoopRight contract completeness checker."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REQUIRED_FIELDS = [
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


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate-loop-contract.py <contract-file>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    if not path.is_file():
        print(f"not found: {path}", file=sys.stderr)
        return 2

    text = normalize(path.read_text(encoding="utf-8"))
    present = [field for field in REQUIRED_FIELDS if field in text]
    missing = [field for field in REQUIRED_FIELDS if field not in text]
    result = {
        "file": str(path),
        "required": REQUIRED_FIELDS,
        "present": present,
        "missing": missing,
        "ok": not missing,
    }
    print(json.dumps(result, indent=2))
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

