#!/usr/bin/env python3
"""Recursively validate LoopRight contracts in Markdown files."""

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


def validate(path: Path) -> dict[str, object]:
    raw_text = path.read_text(encoding="utf-8")
    text = normalize(raw_text)
    present = [field for field in REQUIRED_FIELDS if field in text]
    missing = [field for field in REQUIRED_FIELDS if field not in text]
    return {
        "file": str(path),
        "present": present,
        "missing": missing,
        "ok": not missing,
    }


def is_contract_file(path: Path) -> bool:
    raw_text = path.read_text(encoding="utf-8")
    text = normalize(raw_text)
    has_contract_heading = re.search(r"(?im)^#{1,6}\s+loopright?\s+contract\s*$|^#{1,6}\s+loop\s+contract\s*$", raw_text)
    return bool(has_contract_heading) or all(field in text for field in REQUIRED_FIELDS)


def iter_markdown(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix.lower() in {".md", ".markdown"}:
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
    return sorted(set(files))


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: validate-all-contracts.py <file-or-directory> [...]", file=sys.stderr)
        return 2

    paths = [Path(arg) for arg in argv[1:]]
    files = iter_markdown(paths)
    if not files:
        print("no Markdown files found", file=sys.stderr)
        return 2

    contract_files = [path for path in files if is_contract_file(path)]
    skipped = [str(path) for path in files if path not in contract_files]
    results = [validate(path) for path in contract_files]
    failures = [result for result in results if not result["ok"]]
    print(
        json.dumps(
            {
                "ok": not failures,
                "checked": len(results),
                "skipped": skipped,
                "failures": failures,
            },
            indent=2,
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
