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
    # Core loop heuristics.
    BenchmarkCase(
        "unsafe_unbounded_retry.py",
        ("broad-python-except", "sleep-or-delay", "unbounded-loop"),
    ),
    BenchmarkCase("unsafe_async_fanout.py", ("unbounded-async-fanout",)),
    BenchmarkCase("unsafe_agent_prompt.md", ("agent-loop-without-budget",)),
    BenchmarkCase("unsafe_optuna_tuning.py", ("optuna-without-visible-budget",)),
    BenchmarkCase("unsafe_js_broad_catch.js", ("broad-js-catch",)),
    BenchmarkCase("safe_retry.py", ()),
    BenchmarkCase("safe_poll.py", ()),
    # Agent-framework rulepacks.
    BenchmarkCase(
        "unsafe_langgraph_agent.py",
        ("langgraph-missing-checkpointer", "langgraph-missing-recursion-limit"),
    ),
    BenchmarkCase("safe_langgraph_agent.py", ()),
    BenchmarkCase("unsafe_openai_agents.py", ("openai-agents-missing-max-turns",)),
    BenchmarkCase("safe_openai_agents.py", ()),
    BenchmarkCase("unsafe_crewai_crew.py", ("crewai-missing-iteration-budget",)),
    BenchmarkCase("unsafe_langchain_executor.py", ("langchain-agent-missing-max-iterations",)),
    BenchmarkCase("unsafe_autogen_chat.py", ("autogen-missing-turn-limit",)),
    BenchmarkCase("unsafe_ai_sdk_agent.ts", ("ai-sdk-missing-step-limit",)),
    BenchmarkCase("safe_ai_sdk_agent.ts", ()),
]


def load_scanner() -> ModuleType:
    spec = importlib.util.spec_from_file_location("loopright_discover_loop_risks", SCANNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SCANNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def all_rule_ids(scanner: ModuleType) -> list[str]:
    ids = [str(pattern["id"]) for pattern in scanner.RISK_PATTERNS]
    ids.extend(str(rule["id"]) for rule in scanner.FRAMEWORK_RULES)
    return sorted(ids)


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
        "kind": "safe" if case.fixture.startswith("safe_") else "unsafe",
        "expected": expected,
        "observed": observed,
        "missing": sorted(set(expected) - set(observed)),
        "unexpected": sorted(set(observed) - set(expected)),
        "findings": findings,
        "ok": observed == expected,
    }


def ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 1.0


def summarize(results: list[dict[str, object]], rule_ids: list[str]) -> dict[str, object]:
    true_positive = 0
    false_positive = 0
    false_negative = 0
    per_rule: dict[str, dict[str, int]] = {
        rule_id: {"truePositive": 0, "falsePositive": 0, "falseNegative": 0} for rule_id in rule_ids
    }

    for result in results:
        expected = set(result["expected"])
        observed = set(result["observed"])
        true_positive += len(expected & observed)
        false_positive += len(observed - expected)
        false_negative += len(expected - observed)
        for rule_id in expected & observed:
            per_rule.setdefault(rule_id, {"truePositive": 0, "falsePositive": 0, "falseNegative": 0})["truePositive"] += 1
        for rule_id in observed - expected:
            per_rule.setdefault(rule_id, {"truePositive": 0, "falsePositive": 0, "falseNegative": 0})["falsePositive"] += 1
        for rule_id in expected - observed:
            per_rule.setdefault(rule_id, {"truePositive": 0, "falsePositive": 0, "falseNegative": 0})["falseNegative"] += 1

    by_rule = {}
    for rule_id, counts in sorted(per_rule.items()):
        tp, fp, fn = counts["truePositive"], counts["falsePositive"], counts["falseNegative"]
        by_rule[rule_id] = {
            **counts,
            "precision": ratio(tp, tp + fp),
            "recall": ratio(tp, tp + fn),
            "covered": bool(tp or fn),
        }

    uncovered = sorted(rule_id for rule_id, entry in by_rule.items() if not entry["covered"])
    safe_fixtures = [result for result in results if result["kind"] == "safe"]
    clean_safe = [result for result in safe_fixtures if not result["observed"]]

    return {
        "ok": all(result["ok"] for result in results) and not uncovered,
        "cases": len(results),
        "rules": len(rule_ids),
        "uncoveredRules": uncovered,
        "safeFixtures": len(safe_fixtures),
        "safeFixturesClean": len(clean_safe),
        "truePositive": true_positive,
        "falsePositive": false_positive,
        "falseNegative": false_negative,
        "precision": ratio(true_positive, true_positive + false_positive),
        "recall": ratio(true_positive, true_positive + false_negative),
        "byRule": by_rule,
    }


def render_markdown(payload: dict[str, object]) -> str:
    summary = payload["summary"]
    pct = lambda value: f"{float(value) * 100:.1f}%"
    lines = [
        "# LoopRight Scanner Benchmark Results",
        "",
        "Generated by `python benchmarks/run_loopright_benchmark.py --format md --output benchmarks/RESULTS.md`.",
        "Regenerate after any scanner rule change; CI fails when this file drifts.",
        "",
        "## Headline",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Precision (high-confidence findings) | **{pct(summary['precision'])}** |",
        f"| Recall (high-confidence findings) | **{pct(summary['recall'])}** |",
        f"| Fixtures | {summary['cases']} |",
        f"| Rules exercised | {summary['rules'] - len(summary['uncoveredRules'])}/{summary['rules']} |",
        f"| Safe fixtures with zero findings | {summary['safeFixturesClean']}/{summary['safeFixtures']} |",
        f"| True positives / false positives / false negatives | {summary['truePositive']} / {summary['falsePositive']} / {summary['falseNegative']} |",
        "",
        "Scope note: these are seeded fixtures, not a random sample of production code.",
        "They prove the rules fire where they should and stay quiet on the repaired versions",
        "of the same loops. They do not estimate real-world prevalence.",
        "",
        "## Per-rule results",
        "",
        "| Rule | TP | FP | FN | Precision | Recall |",
        "|---|---|---|---|---|---|",
    ]
    for rule_id, entry in payload["summary"]["byRule"].items():
        lines.append(
            f"| `{rule_id}` | {entry['truePositive']} | {entry['falsePositive']} | "
            f"{entry['falseNegative']} | {pct(entry['precision'])} | {pct(entry['recall'])} |"
        )
    lines.extend(["", "## Per-fixture results", "", "| Fixture | Kind | Expected | Observed | OK |", "|---|---|---|---|---|"])
    for result in payload["results"]:
        expected = ", ".join(f"`{item}`" for item in result["expected"]) or "—"
        observed = ", ".join(f"`{item}`" for item in result["observed"]) or "—"
        lines.append(
            f"| `{result['fixture']}` | {result['kind']} | {expected} | {observed} | "
            f"{'yes' if result['ok'] else 'NO'} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=["json", "md"], default="json", help="Output format")
    parser.add_argument("--output", help="Write benchmark output to this file")
    args = parser.parse_args()

    scanner = load_scanner()
    rule_ids = all_rule_ids(scanner)
    results = [run_case(scanner, case) for case in CASES]
    payload = {
        "benchmark": "loopright-risk-discovery",
        "summary": summarize(results, rule_ids),
        "results": results,
    }

    output = render_markdown(payload) if args.format == "md" else json.dumps(payload, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0 if payload["summary"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
