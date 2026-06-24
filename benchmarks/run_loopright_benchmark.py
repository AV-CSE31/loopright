#!/usr/bin/env python3
"""Run a deterministic LoopRight scanner benchmark over fixture files."""

from __future__ import annotations

import argparse
import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
SCANNER_PATH = ROOT / "skills" / "loopright" / "scripts" / "discover-loop-risks.py"
FIXTURE_DIR = ROOT / "benchmarks" / "fixtures"


@dataclass(frozen=True)
class BenchmarkCase:
    fixture: str
    expected_high_confidence_risks: tuple[str, ...]


CASES = [
    BenchmarkCase(
        "unsafe_unbounded_retry.py",
        ("broad-python-except", "sleep-or-delay", "unbounded-loop"),
    ),
    BenchmarkCase("unsafe_async_fanout.py", ("unbounded-async-fanout",)),
    BenchmarkCase("unsafe_agent_prompt.md", ("agent-loop-without-budget",)),
    BenchmarkCase("safe_retry.py", ()),
    BenchmarkCase("safe_poll.py", ()),
]


def load_scanner() -> ModuleType:
    spec = importlib.util.spec_from_file_location("loopright_discover_loop_risks", SCANNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCANNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_case(scanner: ModuleType, case: BenchmarkCase) -> dict[str, object]:
    path = FIXTURE_DIR / case.fixture
    findings = scanner.discover(path)
    observed = sorted(
        {
            str(finding["risk"])
            for finding in findings
            if finding["confidence"] == "high"
        }
    )
    expected = sorted(case.expected_high_confidence_risks)
    return {
        "fixture": case.fixture,
        "expected": expected,
        "observed": observed,
        "missing": sorted(set(expected) - set(observed)),
        "unexpected": sorted(set(observed) - set(expected)),
        "findings": findings,
        "ok": observed == expected,
    }


def summarize(results: list[dict[str, object]]) -> dict[str, object]:
    true_positive = 0
    false_positive = 0
    false_negative = 0
    for result in results:
        expected = set(result["expected"])
        observed = set(result["observed"])
        true_positive += len(expected & observed)
        false_positive += len(observed - expected)
        false_negative += len(expected - observed)
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 1.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 1.0
    return {
        "ok": all(result["ok"] for result in results),
        "cases": len(results),
        "truePositive": true_positive,
        "falsePositive": false_positive,
        "falseNegative": false_negative,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="Write benchmark JSON to this file")
    args = parser.parse_args()

    scanner = load_scanner()
    results = [run_case(scanner, case) for case in CASES]
    payload = {
        "benchmark": "loopright-risk-discovery",
        "summary": summarize(results),
        "results": results,
    }
    output = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0 if payload["summary"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
