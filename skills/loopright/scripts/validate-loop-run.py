#!/usr/bin/env python3
"""Validate a LoopRight run evidence bundle."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = [
    "schemaVersion",
    "loopId",
    "loopType",
    "objective",
    "contract",
    "run",
    "iterations",
    "verifier",
    "riskControls",
]

REQUIRED_CONTRACT_FIELDS = [
    "objective",
    "state",
    "action",
    "progress",
    "invariant",
    "budget",
    "stopCondition",
    "failureCondition",
    "recovery",
    "evidence",
]

VALID_STATUSES = {"completed", "failed", "stopped", "blocked"}
VALID_CHECK_STATUSES = {"passed", "failed", "skipped"}
VALID_VERIFIER_TYPES = {"deterministic", "human", "independent-review", "agent"}
VALID_VERDICTS = {"pass", "fail", "approved", "rejected"}
VALID_PERMISSION_BOUNDARIES = {"read-only", "dry-run", "paper", "approved-live", "none"}
BUDGET_FIELDS = {"maxIterations", "maxSeconds", "maxCostUsd", "maxConcurrency", "deadline"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class Reporter:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def require_object(value: Any, path: str, reporter: Reporter) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    reporter.error(f"{path} must be an object")
    return {}


def require_array(value: Any, path: str, reporter: Reporter) -> list[Any]:
    if isinstance(value, list):
        return value
    reporter.error(f"{path} must be an array")
    return []


def require_string(obj: dict[str, Any], field: str, path: str, reporter: Reporter) -> str:
    value = obj.get(field)
    if not is_non_empty_string(value):
        reporter.error(f"{path}.{field} must be a non-empty string")
        return ""
    return value.strip()


def parse_timestamp(value: Any, path: str, reporter: Reporter) -> datetime | None:
    if not is_non_empty_string(value):
        reporter.error(f"{path} must be an ISO-8601 timestamp")
        return None
    text = value.strip()
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        reporter.error(f"{path} must be an ISO-8601 timestamp")
        return None


def validate_budget(budget: Any, reporter: Reporter) -> None:
    budget_obj = require_object(budget, "contract.budget", reporter)
    if not budget_obj:
        return
    visible_fields = BUDGET_FIELDS.intersection(budget_obj)
    if not visible_fields:
        reporter.error("contract.budget must include at least one hard limit")

    for field in ["maxIterations", "maxSeconds", "maxCostUsd", "maxConcurrency"]:
        if field not in budget_obj:
            continue
        value = budget_obj[field]
        if not isinstance(value, (int, float)) or value <= 0:
            reporter.error(f"contract.budget.{field} must be a positive number")

    if "deadline" in budget_obj:
        parse_timestamp(budget_obj["deadline"], "contract.budget.deadline", reporter)


def validate_contract(contract: Any, objective: str, reporter: Reporter) -> dict[str, Any]:
    contract_obj = require_object(contract, "contract", reporter)
    for field in REQUIRED_CONTRACT_FIELDS:
        if field == "budget":
            if field not in contract_obj:
                reporter.error("contract.budget is required")
            else:
                validate_budget(contract_obj[field], reporter)
        else:
            require_string(contract_obj, field, "contract", reporter)

    contract_objective = contract_obj.get("objective")
    if is_non_empty_string(objective) and is_non_empty_string(contract_objective):
        if objective.strip() != contract_objective.strip():
            reporter.warn("objective and contract.objective differ; make sure the run proves the same target")
    return contract_obj


def validate_run(run: Any, contract: dict[str, Any], iteration_count: int, reporter: Reporter) -> dict[str, Any]:
    run_obj = require_object(run, "run", reporter)
    status = run_obj.get("status")
    if status not in VALID_STATUSES:
        reporter.error(f"run.status must be one of {sorted(VALID_STATUSES)}")
    require_string(run_obj, "stopReason", "run", reporter)

    started = parse_timestamp(run_obj.get("startedAt"), "run.startedAt", reporter)
    ended = parse_timestamp(run_obj.get("endedAt"), "run.endedAt", reporter)
    if started is not None and ended is not None and ended < started:
        reporter.error("run.endedAt must be after run.startedAt")

    iterations_used = run_obj.get("iterationsUsed")
    if not isinstance(iterations_used, int) or iterations_used < 0:
        reporter.error("run.iterationsUsed must be a non-negative integer")
        iterations_used = None
    elif iterations_used > iteration_count:
        reporter.error("run.iterationsUsed cannot exceed the number of iteration records")

    budget = contract.get("budget") if isinstance(contract, dict) else {}
    if isinstance(budget, dict) and isinstance(iterations_used, int):
        max_iterations = budget.get("maxIterations")
        if isinstance(max_iterations, (int, float)) and iterations_used > max_iterations:
            reporter.error("run.iterationsUsed exceeds contract.budget.maxIterations")

    for field in ["secondsUsed", "costUsd"]:
        if field in run_obj:
            value = run_obj[field]
            if not isinstance(value, (int, float)) or value < 0:
                reporter.error(f"run.{field} must be a non-negative number")

    if isinstance(budget, dict):
        max_seconds = budget.get("maxSeconds")
        if isinstance(max_seconds, (int, float)) and isinstance(run_obj.get("secondsUsed"), (int, float)):
            if run_obj["secondsUsed"] > max_seconds:
                reporter.error("run.secondsUsed exceeds contract.budget.maxSeconds")
        max_cost = budget.get("maxCostUsd")
        if isinstance(max_cost, (int, float)) and isinstance(run_obj.get("costUsd"), (int, float)):
            if run_obj["costUsd"] > max_cost:
                reporter.error("run.costUsd exceeds contract.budget.maxCostUsd")

    return run_obj


def validate_checks(checks: Any, path: str, reporter: Reporter) -> int:
    check_list = require_array(checks, path, reporter)
    passed = 0
    for index, check in enumerate(check_list):
        check_path = f"{path}[{index}]"
        check_obj = require_object(check, check_path, reporter)
        require_string(check_obj, "name", check_path, reporter)
        status = check_obj.get("status")
        if status not in VALID_CHECK_STATUSES:
            reporter.error(f"{check_path}.status must be one of {sorted(VALID_CHECK_STATUSES)}")
        if status == "passed":
            passed += 1
    return passed


def validate_iterations(iterations: Any, reporter: Reporter) -> tuple[list[dict[str, Any]], int]:
    iteration_list = require_array(iterations, "iterations", reporter)
    if not iteration_list:
        reporter.error("iterations must include at least one iteration record")
        return [], 0

    seen_indexes: set[int] = set()
    passed_checks = 0
    failure_signatures: dict[str, int] = {}
    valid_iterations: list[dict[str, Any]] = []

    for array_index, iteration in enumerate(iteration_list):
        path = f"iterations[{array_index}]"
        iteration_obj = require_object(iteration, path, reporter)
        valid_iterations.append(iteration_obj)

        index = iteration_obj.get("index")
        if not isinstance(index, int) or index < 1:
            reporter.error(f"{path}.index must be a positive integer")
        elif index in seen_indexes:
            reporter.error(f"{path}.index must be unique")
        else:
            seen_indexes.add(index)

        for field in ["hypothesis", "action", "progress", "status"]:
            require_string(iteration_obj, field, path, reporter)

        status = iteration_obj.get("status")
        if status not in {"passed", "failed", "changed", "no-progress"}:
            reporter.error(f"{path}.status must be passed, failed, changed, or no-progress")

        checks = iteration_obj.get("checks", [])
        passed_checks += validate_checks(checks, f"{path}.checks", reporter)

        signature = iteration_obj.get("failureSignature")
        if is_non_empty_string(signature):
            failure_signatures[signature.strip()] = failure_signatures.get(signature.strip(), 0) + 1

    for signature, count in failure_signatures.items():
        if count >= 3:
            reporter.warn(f"failureSignature '{signature}' appears {count} times; verify the no-progress stop rule")

    return valid_iterations, passed_checks


def validate_artifacts(artifacts: Any, reporter: Reporter) -> list[dict[str, Any]]:
    if artifacts is None:
        return []
    artifact_list = require_array(artifacts, "artifacts", reporter)
    valid_artifacts: list[dict[str, Any]] = []
    for index, artifact in enumerate(artifact_list):
        path = f"artifacts[{index}]"
        artifact_obj = require_object(artifact, path, reporter)
        valid_artifacts.append(artifact_obj)
        require_string(artifact_obj, "kind", path, reporter)
        has_path = is_non_empty_string(artifact_obj.get("path"))
        has_url = is_non_empty_string(artifact_obj.get("url"))
        if not has_path and not has_url:
            reporter.error(f"{path} must include path or url")
        sha = artifact_obj.get("sha256")
        if sha is None:
            reporter.warn(f"{path}.sha256 is missing; attach hashes for durable evidence when possible")
        elif not (isinstance(sha, str) and SHA256_RE.match(sha)):
            reporter.error(f"{path}.sha256 must be a lowercase 64-character hex digest")
    return valid_artifacts


def validate_verifier(verifier: Any, reporter: Reporter) -> dict[str, Any]:
    verifier_obj = require_object(verifier, "verifier", reporter)
    verifier_type = verifier_obj.get("type")
    verdict = verifier_obj.get("verdict")
    if verifier_type not in VALID_VERIFIER_TYPES:
        reporter.error(f"verifier.type must be one of {sorted(VALID_VERIFIER_TYPES)}")
    if verdict not in VALID_VERDICTS:
        reporter.error(f"verifier.verdict must be one of {sorted(VALID_VERDICTS)}")
    require_string(verifier_obj, "name", "verifier", reporter)
    if verifier_type == "agent":
        reporter.warn("verifier.type is agent; use deterministic or independent verification for consequential loops")
    return verifier_obj


def validate_risk_controls(risk_controls: Any, reporter: Reporter) -> dict[str, Any]:
    controls = require_object(risk_controls, "riskControls", reporter)
    boundary = controls.get("permissionBoundary")
    if boundary not in VALID_PERMISSION_BOUNDARIES:
        reporter.error(f"riskControls.permissionBoundary must be one of {sorted(VALID_PERMISSION_BOUNDARIES)}")
    if not isinstance(controls.get("killSwitchChecked"), bool):
        reporter.error("riskControls.killSwitchChecked must be boolean")

    side_effects = require_array(controls.get("sideEffects", []), "riskControls.sideEffects", reporter)
    if side_effects and boundary == "none":
        reporter.error("riskControls.permissionBoundary cannot be none when sideEffects are present")

    for index, effect in enumerate(side_effects):
        path = f"riskControls.sideEffects[{index}]"
        effect_obj = require_object(effect, path, reporter)
        require_string(effect_obj, "kind", path, reporter)
        require_string(effect_obj, "target", path, reporter)
        if not is_non_empty_string(effect_obj.get("idempotencyKey")) and not is_non_empty_string(effect_obj.get("compensation")):
            reporter.error(f"{path} must include idempotencyKey or compensation")
        if not is_non_empty_string(effect_obj.get("auditRef")):
            reporter.warn(f"{path}.auditRef is missing; side effects should be auditable")
    return controls


def validate_trace(trace: Any, reporter: Reporter) -> None:
    if trace is None:
        reporter.warn("trace is missing; include traceId/spanCount when a runtime trace exists")
        return
    trace_obj = require_object(trace, "trace", reporter)
    require_string(trace_obj, "traceId", "trace", reporter)
    span_count = trace_obj.get("spanCount")
    if not isinstance(span_count, int) or span_count < 1:
        reporter.error("trace.spanCount must be a positive integer")


def validate_evaluations(evaluations: Any, loop_type: str, reporter: Reporter) -> None:
    expects_eval = any(term in loop_type.lower() for term in ["ml", "tuning", "benchmark", "research"])
    if evaluations is None:
        if expects_eval:
            reporter.warn("evaluations are missing for an evaluation-heavy loop type")
        return
    evaluation_list = require_array(evaluations, "evaluations", reporter)
    if expects_eval and not evaluation_list:
        reporter.warn("evaluations are empty for an evaluation-heavy loop type")
    for index, evaluation in enumerate(evaluation_list):
        path = f"evaluations[{index}]"
        evaluation_obj = require_object(evaluation, path, reporter)
        for field in ["name", "metric", "status"]:
            require_string(evaluation_obj, field, path, reporter)
        if evaluation_obj.get("status") not in {"passed", "failed", "skipped"}:
            reporter.error(f"{path}.status must be passed, failed, or skipped")


def validate_bundle(data: Any) -> dict[str, Any]:
    reporter = Reporter()
    if not isinstance(data, dict):
        return {
            "ok": False,
            "errors": ["bundle must be a JSON object"],
            "warnings": [],
            "summary": {},
        }

    for field in REQUIRED_TOP_LEVEL:
        if field not in data:
            reporter.error(f"{field} is required")

    if data.get("schemaVersion") != 1:
        reporter.error("schemaVersion must be 1")

    for field in ["loopId", "loopType", "objective"]:
        require_string(data, field, "<root>", reporter)

    objective = data.get("objective", "")
    loop_type = data.get("loopType", "")
    iterations, passed_checks = validate_iterations(data.get("iterations", []), reporter)
    contract = validate_contract(data.get("contract"), str(objective), reporter)
    run = validate_run(data.get("run"), contract, len(iterations), reporter)
    artifacts = validate_artifacts(data.get("artifacts"), reporter)
    verifier = validate_verifier(data.get("verifier"), reporter)
    controls = validate_risk_controls(data.get("riskControls"), reporter)
    validate_trace(data.get("trace"), reporter)
    validate_evaluations(data.get("evaluations"), str(loop_type), reporter)

    status = run.get("status")
    verdict = verifier.get("verdict")
    if status == "completed" and verdict not in {"pass", "approved"}:
        reporter.error("completed runs require verifier.verdict pass or approved")
    if status == "completed" and not artifacts and passed_checks == 0:
        reporter.error("completed runs require at least one artifact or passed check")
    if status == "completed" and controls.get("killSwitchChecked") is not True:
        reporter.error("completed consequential runs must confirm riskControls.killSwitchChecked")

    summary = {
        "loopId": data.get("loopId"),
        "loopType": loop_type,
        "status": status,
        "iterations": len(iterations),
        "passedChecks": passed_checks,
        "artifacts": len(artifacts),
        "sideEffects": len(controls.get("sideEffects", [])) if isinstance(controls, dict) else 0,
    }
    return {
        "ok": not reporter.errors,
        "errors": reporter.errors,
        "warnings": reporter.warnings,
        "summary": summary,
    }


def load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return None, str(error)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a LoopRight run evidence bundle.")
    parser.add_argument("bundle", help="Path to a LoopRight run evidence JSON file")
    parser.add_argument("--fail-on-warning", action="store_true", help="Exit 1 when warnings are present")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    path = Path(args.bundle)
    data, load_error = load_json(path)
    if load_error is not None:
        result = {
            "ok": False,
            "errors": [f"cannot read evidence bundle: {load_error}"],
            "warnings": [],
            "summary": {"file": str(path)},
        }
    else:
        result = validate_bundle(data)
        result["summary"]["file"] = str(path)

    print(json.dumps(result, indent=2))
    if not result["ok"]:
        return 1
    if args.fail_on_warning and result["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
