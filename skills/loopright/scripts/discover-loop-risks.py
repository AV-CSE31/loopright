#!/usr/bin/env python3
"""Heuristically discover dangerous or under-specified loop patterns."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".mypy_cache", ".pytest_cache"}
TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
}


RISK_PATTERNS = [
    {
        "id": "unbounded-loop",
        "severity": "P1",
        "regex": re.compile(r"\bwhile\s+True\s*:|\bwhile\s*\(\s*true\s*\)|\bfor\s*\(\s*;\s*;\s*\)"),
        "message": "Potential unbounded loop. Look for deadline, max iterations, cancellation, or terminal state.",
    },
    {
        "id": "broad-python-except",
        "severity": "P1",
        "regex": re.compile(r"^\s*except\s*(?:Exception|BaseException)?\s*(?:as\s+\w+)?\s*:", re.MULTILINE),
        "message": "Broad exception catch can hide permanent failures, especially inside retry loops.",
    },
    {
        "id": "broad-js-catch",
        "severity": "P2",
        "regex": re.compile(r"\bcatch\s*\(\s*(?:error|err|e)\s*\)"),
        "message": "Broad catch needs a transient-failure allowlist when used for retries.",
    },
    {
        "id": "sleep-or-delay",
        "severity": "P2",
        "regex": re.compile(r"\b(?:time\.sleep|asyncio\.sleep|setTimeout|sleep|delay)\s*\("),
        "message": "Sleep or delay near loop code should have a deadline, cancellation path, and terminal failure states.",
    },
    {
        "id": "unbounded-async-fanout",
        "severity": "P1",
        "regex": re.compile(r"\basyncio\.gather\s*\(|\bPromise\.all\s*\("),
        "message": "Async fan-out may be unbounded. Look for semaphore, queue, worker pool, or capacity limiter.",
    },
    {
        "id": "optuna-without-visible-budget",
        "severity": "P1",
        "regex": re.compile(r"\bstudy\.optimize\s*\((?![^)]*(?:n_trials|timeout)\s*=)", re.DOTALL),
        "message": "Optuna optimize call has no visible n_trials or timeout budget in the call.",
    },
    {
        "id": "agent-loop-without-budget",
        "severity": "P1",
        "regex": re.compile(r"\b(?:keep\s+(?:trying|editing|fixing|improving)|repeat\s+until|until\s+it\s+(?:works|passes)|iterate\s+until)\b", re.IGNORECASE),
        "message": "Agent loop wording needs a cycle budget, stop condition, and repeated-failure guard.",
    },
]


BUDGET_TERMS = re.compile(
    r"\b(max|limit|deadline|timeout|cancel|cancellation|budget|attempt|poll|terminal|stop|until|elapsed|ttl)\b",
    re.IGNORECASE,
)


def iter_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
            files.append(path)
    return files


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def window(text: str, offset: int, radius: int = 250) -> str:
    return text[max(0, offset - radius): offset + radius]


def discover(path: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return findings

    for pattern in RISK_PATTERNS:
        for match in pattern["regex"].finditer(text):
            context = window(text, match.start())
            has_budget_language = bool(BUDGET_TERMS.search(context))
            confidence = "medium" if has_budget_language else "high"
            if pattern["id"] in {"sleep-or-delay", "broad-js-catch"} and has_budget_language:
                confidence = "low"
            findings.append(
                {
                    "file": str(path),
                    "line": line_number(text, match.start()),
                    "risk": pattern["id"],
                    "severity": pattern["severity"],
                    "confidence": confidence,
                    "message": pattern["message"],
                    "matched": match.group(0).strip().splitlines()[0][:120],
                }
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Files or directories to scan")
    parser.add_argument("--fail-on-risk", action="store_true", help="Exit 1 when high-confidence findings exist")
    args = parser.parse_args()

    findings: list[dict[str, object]] = []
    for raw_path in args.paths:
        for file_path in iter_files(Path(raw_path)):
            findings.extend(discover(file_path))

    high_confidence = [finding for finding in findings if finding["confidence"] == "high"]
    print(
        json.dumps(
            {
                "ok": not high_confidence,
                "findings": findings,
                "summary": {
                    "total": len(findings),
                    "highConfidence": len(high_confidence),
                },
            },
            indent=2,
        )
    )
    return 1 if args.fail_on_risk and high_confidence else 0


if __name__ == "__main__":
    raise SystemExit(main())

