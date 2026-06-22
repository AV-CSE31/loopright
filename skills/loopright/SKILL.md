---
name: loopright
description: Design, implement, refactor, or review safe, bounded, measurable, failure-aware loops. Use for Python, JavaScript, TypeScript, retries, polling, async concurrency, data processing, ML tuning, optimization, iterative code repair, agent tool-use loops, and durable workflow design. Do not use for simple one-pass code that requires no iteration.
---

# LoopRight

Write loops right: bounded by design, measured by progress, completed with evidence.

Use this skill whenever a task depends on repeated action, convergence, retries, polling, batching, async fan-out, optimization, training, iterative repair, or an agentic tool loop.

## Workflow

1. Inspect the repository before designing the loop.
2. Establish a loop contract before editing code.
3. Classify the primary loop type.
4. Select the smallest correct primitive already available in the project.
5. Design termination and failure handling before implementation.
6. Implement the loop with observable progress and explicit budgets.
7. Add tests for termination, failure, edge cases, and completion evidence.
8. Verify the loop with tests, measurements, logs, artifacts, or review output.

## Loop Contract

Answer these before implementation:

| Element | Required answer |
|---|---|
| Objective | What measurable result must the loop achieve? |
| State | What changes between iterations? |
| Action | What operation occurs each iteration? |
| Progress | What observable value proves movement? |
| Invariant | What must remain true during every iteration? |
| Budget | What limits iterations, time, cost, memory, or concurrency? |
| Stop condition | When does normal execution stop? |
| Failure condition | What makes continuing unsafe or useless? |
| Recovery | What can safely change after failure or stagnation? |
| Evidence | What proves the final result is acceptable? |

Do not proceed from vague goals such as "retry until successful", "keep refining", "improve performance", or "make it optimal". Convert them to measurable constraints first.

## Primitive Selection

Prefer existing project conventions and mature libraries:

| Requirement | Preferred primitive |
|---|---|
| Known finite count | `for` with `range` or equivalent |
| Iterate over a collection | Native iterator or readable comprehension |
| Continue until condition | Bounded `while` loop |
| Retry transient failures | Existing retry library or runtime-native retry |
| Poll external status | Deadline, bounded delay, cancellation, and jitter |
| Independent async I/O | Task group or existing async framework primitive |
| Bounded parallel work | Semaphore or capacity limiter with task group |
| Hyperparameter optimization | Existing optimizer such as Optuna or project equivalent |
| Model training | Existing ML framework training loop |
| Crash-resumable workflow | Existing durable execution runtime |
| Agent tool loop | Explicit action, budget, evidence, and stop policy |

Do not reimplement task groups, retry frameworks, workflow persistence, distributed locks, schedulers, experiment trackers, or hyperparameter samplers.

## Mandatory Rules

- Define at least one hard termination boundary: max iterations, deadline, cancellation signal, input exhaustion, resource budget, convergence threshold, or terminal state.
- Treat unbounded `while True` as invalid unless it has an explicit external lifetime and cancellation contract.
- Retry only known transient failures, never every exception.
- Add backoff and jitter when many workers may retry or poll the same service.
- Make cancellation and cleanup safe for async or concurrent loops.
- Record progress in a way tests or operators can inspect.
- Claim completion only when evidence exists.
- Avoid introducing LLM decisions when deterministic checks can decide.

## References

Load only the relevant reference:

- `references/loop-patterns.md`: baseline patterns, contracts, and termination.
- `references/retries-and-polling.md`: retry, polling, backoff, jitter, and idempotency.
- `references/async-concurrency.md`: async task groups, cancellation, and bounded parallelism.
- `references/ml-tuning.md`: training, evaluation, optimization, pruning, and experiment evidence.
- `references/agent-loops.md`: coding-agent, tool-use, and iterative repair loops.
- `references/review-rubric.md`: review checklist and severity guidance.

## Script

Use `scripts/validate-loop-contract.py <file>` to check whether a Markdown or text contract mentions the required LoopRight contract fields. This script is a lightweight completeness check, not a proof of correctness.

