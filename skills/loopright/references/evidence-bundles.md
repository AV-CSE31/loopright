# Loop Evidence Bundles

Use a Loop Evidence Bundle when a loop has run and someone needs to prove it stopped for the right reason, stayed inside budget, and produced acceptable evidence.

This is most useful for agent repair loops, ML tuning, benchmark loops, distributed backfills, polling jobs, and autonomous loops with connector-backed side effects.

## Bundle Shape

Use `templates/loop-run-evidence-template.json` as the starting point. A valid bundle includes:

- `schemaVersion`: currently `1`.
- `loopId`: stable id for this loop run.
- `loopType`: pattern name such as `retry-loop`, `agent-repair-loop`, `ml-tuning-loop`, or `autonomous-decision-loop`.
- `objective`: measurable result the run tried to achieve.
- `contract`: objective, state, action, progress, invariant, budget, stop condition, failure condition, recovery, and evidence.
- `run`: start/end time, status, stop reason, iterations used, elapsed seconds, and optional cost.
- `iterations`: one record per cycle with hypothesis, action, progress, status, checks, and optional failure signature.
- `artifacts`: durable files or URLs that prove the result.
- `verifier`: deterministic, human, independent-review, or agent verifier with pass/fail or approval verdict.
- `riskControls`: permission boundary, kill-switch confirmation, and side-effect audit/idempotency records.
- `trace`: optional trace id, span count, and provider when runtime tracing exists.
- `evaluations`: optional metric checks for benchmark, research, ML, and optimization loops.

## Validation

Run:

```bash
python scripts/loopright.py validate-run path/to/loop-run.json
```

Use `--fail-on-warning` in CI when missing hashes, missing traces, or weak verifier choices should block the change:

```bash
python scripts/loopright.py validate-run path/to/loop-run.json --fail-on-warning
```

The validator uses only Python's standard library and sibling files inside the skill folder.

## What To Treat As Errors

Reject a bundle when:

- Required top-level fields are missing.
- The contract omits a hard budget.
- `run.iterationsUsed` exceeds the budget or the number of recorded iterations.
- `run.secondsUsed` or `run.costUsd` exceeds the budget.
- A completed run lacks a passing/approved verifier verdict.
- A completed run has no passed check and no artifact.
- Side effects exist without a permission boundary.
- Side effects lack idempotency keys or compensation records.
- Completion claims omit kill-switch confirmation.

## What To Treat As Warnings

Escalate but do not automatically reject when:

- Artifact hashes are missing.
- Runtime trace metadata is missing.
- An agent is the verifier for a consequential loop.
- The same failure signature appears three or more times.
- Evaluation-heavy loops omit evaluation records.

## Evidence Quality Bar

Prefer evidence that is independently checkable:

- Test command and exact result.
- Metric table with baseline, threshold, and observed value.
- Trace id or span count from the runtime.
- Artifact path or URL plus hash.
- Audit record for each side effect.
- Human approval record when deterministic proof is impossible.

Do not accept "the agent says it worked" as evidence when a command, metric, artifact, trace, or independent reviewer can verify the result.
