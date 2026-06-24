#!/usr/bin/env python3
"""LoopRight command front door.

This script is intentionally self-contained inside the skill folder. It uses only
Python standard-library modules and sibling LoopRight scripts.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REFERENCE_DIR = SKILL_DIR / "references"
TEMPLATE_PATH = SKILL_DIR / "templates" / "loop-contract-template.md"


LOOP_TERMS = re.compile(
    r"\b(loop|loops|retry|poll|batch|worker|workers|training|tuning|optimize|repair|iterate|iteration|budget|stop condition)\b",
    re.IGNORECASE,
)


REPAIR_BY_RISK = {
    "unbounded-loop": "Add a hard termination boundary: max iterations, deadline, cancellation signal, terminal state, or input exhaustion.",
    "broad-python-except": "Replace the broad catch with a transient-failure allowlist and route permanent failures to fail-fast or dead-letter behavior.",
    "broad-js-catch": "Classify caught errors before retrying; retry only transient cases and preserve permanent failures.",
    "sleep-or-delay": "Attach every delay to a deadline, cancellation path, terminal failure states, and observable progress.",
    "unbounded-async-fanout": "Replace unbounded fan-out with a semaphore, queue, worker pool, or task group with a visible concurrency limit.",
    "optuna-without-visible-budget": "Add n_trials or timeout, baseline metrics, validation split identity, pruning policy, and final comparison evidence.",
    "agent-loop-without-budget": "Add a cycle budget, changed-hypothesis requirement, no-progress stop, and deterministic completion check.",
}


EVIDENCE_BY_RISK = {
    "unbounded-loop": "Test normal completion plus budget exhaustion, and record the stop reason.",
    "broad-python-except": "Test transient failure, permanent failure, and retry-budget exhaustion.",
    "broad-js-catch": "Test transient failure, permanent failure, and retry-budget exhaustion.",
    "sleep-or-delay": "Show deadline/cancellation behavior and terminal failure handling.",
    "unbounded-async-fanout": "Measure max active work and prove cancellation or partial-failure cleanup.",
    "optuna-without-visible-budget": "Save baseline, trial budget, best trial, validation split, seed, and final metric table.",
    "agent-loop-without-budget": "Record cycles used, hypotheses changed, check command, and repeated-failure stop status.",
}


def load_sibling(script_name: str, module_name: str) -> ModuleType:
    script_path = SCRIPT_DIR / script_name
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_output(text: str, output: str | None) -> None:
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text, end="" if text.endswith("\n") else "\n")


def run_sibling(script_name: str, args: list[str]) -> int:
    return subprocess.call([sys.executable, str(SCRIPT_DIR / script_name), *args])


def command_scan(args: argparse.Namespace) -> int:
    scanner = load_sibling("discover-loop-risks.py", "loopright_discover_loop_risks")
    findings: list[dict[str, object]] = []
    for raw_path in args.paths:
        for file_path in scanner.iter_files(Path(raw_path)):
            findings.extend(scanner.discover(file_path))
    payload = scanner.build_payload(findings)
    write_output(scanner.render_payload(payload, args.format), args.output)
    return 1 if args.fail_on_risk and payload["summary"]["highConfidence"] else 0


def read_doctor_input(args: argparse.Namespace) -> tuple[str, str]:
    if args.text is not None:
        return args.text, "<text>"
    if args.input is None or args.input == "-":
        return sys.stdin.read(), "<stdin>"
    path = Path(args.input)
    return path.read_text(encoding="utf-8"), str(path)


def doctor_verdict(text: str, findings: list[dict[str, object]]) -> str:
    high = [finding for finding in findings if finding["confidence"] == "high"]
    if any(finding["severity"] == "P1" for finding in high):
        return "Unsafe to run"
    if findings:
        return "Repair needed"
    if not LOOP_TERMS.search(text):
        return "Not actually a loop"
    return "Ready"


def build_doctor_report(text: str, source: str, findings: list[dict[str, object]]) -> dict[str, object]:
    verdict = doctor_verdict(text, findings)
    diagnosis = []
    for finding in findings[:5]:
        diagnosis.append(
            (
                f"{finding['severity']} {finding['risk']} at "
                f"{finding['file']}:{finding['line']}: {finding['message']} "
                f"(confidence: {finding['confidence']}; matched: {finding['matched']})"
            )
        )
    if not diagnosis and verdict == "Ready":
        diagnosis.append("No material LoopRight risk matched the current heuristic rules.")
    if not diagnosis and verdict == "Not actually a loop":
        diagnosis.append("No repeated-action contract is visible in the supplied text.")

    repair_items = []
    evidence_items = []
    seen_risks = []
    for finding in findings:
        risk = str(finding["risk"])
        if risk in seen_risks:
            continue
        seen_risks.append(risk)
        repair_items.append(REPAIR_BY_RISK.get(risk, "Complete the missing LoopRight contract fields before running."))
        evidence_items.append(EVIDENCE_BY_RISK.get(risk, "Provide concrete checks, logs, metrics, or artifacts before claiming completion."))

    if not repair_items and verdict == "Ready":
        repair_items.append("Keep the existing contract; verify objective, progress, budget, stop condition, failure handling, and evidence before shipping.")
    if not repair_items and verdict == "Not actually a loop":
        repair_items.append("Use a one-pass workflow unless new feedback changes later actions.")
    if not evidence_items:
        evidence_items.append("Provide the command, metric, artifact, or review record that proves the final state.")

    return {
        "source": source,
        "verdict": verdict,
        "diagnosis": diagnosis,
        "minimalRepair": repair_items,
        "requiredEvidence": evidence_items,
        "findings": findings,
    }


def render_doctor_markdown(report: dict[str, object]) -> str:
    lines = [
        "## Loop Doctor",
        "",
        f"Verdict: {report['verdict']}",
        "",
        "Diagnosis:",
    ]
    for item in report["diagnosis"]:
        lines.append(f"- {item}")
    lines.extend(["", "Minimal repair:"])
    for item in report["minimalRepair"]:
        lines.append(f"- {item}")
    lines.extend(["", "Required evidence:"])
    for item in report["requiredEvidence"]:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def command_doctor(args: argparse.Namespace) -> int:
    scanner = load_sibling("discover-loop-risks.py", "loopright_discover_loop_risks")
    text, source = read_doctor_input(args)
    findings = scanner.discover_text(text, source)
    report = build_doctor_report(text, source, findings)
    if args.format == "json":
        output = json.dumps(report, indent=2)
    else:
        output = render_doctor_markdown(report)
    write_output(output, args.output)
    return 1 if report["verdict"] == "Unsafe to run" and args.fail_on_risk else 0


def command_validate_contract(args: argparse.Namespace) -> int:
    return run_sibling("validate-loop-contract.py", [args.contract_file])


def command_validate_contracts(args: argparse.Namespace) -> int:
    return run_sibling("validate-all-contracts.py", args.paths)


def command_validate_catalog(args: argparse.Namespace) -> int:
    catalog = args.catalog_json or str(REFERENCE_DIR / "pattern-catalog.json")
    return run_sibling("validate-pattern-catalog.py", [catalog])


def command_catalog(args: argparse.Namespace) -> int:
    files = {
        "json": REFERENCE_DIR / "pattern-catalog.json",
        "md": REFERENCE_DIR / "pattern-catalog.md",
        "llms": REFERENCE_DIR / "llms.txt",
    }
    write_output(files[args.format].read_text(encoding="utf-8"), args.output)
    return 0


def command_template(args: argparse.Namespace) -> int:
    write_output(TEMPLATE_PATH.read_text(encoding="utf-8"), args.output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LoopRight utilities for safe loop design, review, and validation.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Discover dangerous or under-specified loops")
    scan.add_argument("paths", nargs="+", help="Files or directories to scan")
    scan.add_argument("--format", choices=["json", "sarif", "md"], default="json")
    scan.add_argument("--output", help="Write output to a file")
    scan.add_argument("--fail-on-risk", action="store_true", help="Exit 1 when high-confidence findings exist")
    scan.set_defaults(func=command_scan)

    doctor = subparsers.add_parser("doctor", help="Generate a Loop Doctor report for text or a file")
    doctor.add_argument("input", nargs="?", help="File to inspect, or '-' for stdin")
    doctor.add_argument("--text", help="Inline text to inspect")
    doctor.add_argument("--format", choices=["md", "json"], default="md")
    doctor.add_argument("--output", help="Write output to a file")
    doctor.add_argument("--fail-on-risk", action="store_true", help="Exit 1 when the verdict is Unsafe to run")
    doctor.set_defaults(func=command_doctor)

    validate_contract = subparsers.add_parser("validate-contract", help="Validate one LoopRight contract")
    validate_contract.add_argument("contract_file")
    validate_contract.set_defaults(func=command_validate_contract)

    validate_contracts = subparsers.add_parser("validate-contracts", help="Validate LoopRight contracts in files or folders")
    validate_contracts.add_argument("paths", nargs="+")
    validate_contracts.set_defaults(func=command_validate_contracts)

    validate_catalog = subparsers.add_parser("validate-catalog", help="Validate the pattern catalog")
    validate_catalog.add_argument("catalog_json", nargs="?")
    validate_catalog.set_defaults(func=command_validate_catalog)

    catalog = subparsers.add_parser("catalog", help="Print the bundled pattern catalog")
    catalog.add_argument("--format", choices=["json", "md", "llms"], default="md")
    catalog.add_argument("--output", help="Write output to a file")
    catalog.set_defaults(func=command_catalog)

    template = subparsers.add_parser("template", help="Print the LoopRight contract template")
    template.add_argument("--output", help="Write output to a file")
    template.set_defaults(func=command_template)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
