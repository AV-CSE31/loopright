# LoopRight Pattern Catalog

Engineering-grade loop patterns for designing, reviewing, repairing, and validating bounded, measurable, failure-aware loops.

Updated: 2026-06-24

## Patterns

### LR-001 - Retry Loop

Retry transient failures without duplicating side effects or hiding terminal errors.

Category: `reliability`

Use when:

Use when an operation can fail temporarily and can be safely attempted again under a bounded policy.

Prompt:

```text
Review or implement this retry loop with a transient-failure allowlist, attempt or deadline budget, backoff with jitter when shared systems are involved, idempotency for side effects, and final evidence that records attempts and stop reason.
```

Contract:

| Element | Answer |
|---|---|
| Objective | Complete one operation or fail with a clear terminal reason. |
| State | Attempt count, delay, last transient error, idempotency key, elapsed time. |
| Action | Run the operation once. |
| Progress | Attempt count advances and terminal success or failure becomes known. |
| Invariant | The operation target and idempotency identity remain stable across retries. |
| Budget | Maximum attempts, deadline, cost, or caller cancellation. |
| Stop Condition | Operation succeeds or returns a known duplicate-success terminal status. |
| Failure Condition | Permanent error, invalid input, exhausted budget, cancellation, or unsafe side-effect risk. |
| Recovery | Back off, jitter, preserve diagnostics, and retry only allowed transient failures. |
| Evidence | Attempt count, elapsed time, final status, and preserved root cause on failure. |

Red flags:

- Unbounded while true retry
- Bare catch or broad exception retry
- Retrying validation, auth, corrupt data, or programming errors
- No idempotency key for mutating external calls
- Resetting diagnostics on each attempt

Verification:

- Retry budget and failure policy are proven.
- Tests cover first-try success, transient-then-success, budget exhaustion, and permanent errors that are not retried.

Tests:

- Succeeds without retry
- Retries allowlisted transient failure and then succeeds
- Stops at max attempts or deadline
- Does not retry permanent failures
- Preserves original error context

Failure modes:

- Runaway cost or traffic
- Duplicate writes
- Masked permanent failures
- Thundering herd
- Lost diagnostics

Related patterns:

- polling-loop
- durable-workflow-loop
- distributed-backfill-loop

### LR-002 - Polling Loop

Wait for external state without hanging forever or missing terminal failure states.

Category: `reliability`

Use when:

Use when a system must repeatedly read external status until a terminal state is reached.

Prompt:

```text
Design or review this polling loop with a deadline or max polls, terminal success and failure states, delay policy, cancellation behavior, and evidence of final status.
```

Contract:

| Element | Answer |
|---|---|
| Objective | Wait until a known resource reaches an explicit terminal status. |
| State | Current status, poll count, elapsed time, last response, cancellation signal. |
| Action | Fetch current status once. |
| Progress | Poll count advances and status transitions are observed. |
| Invariant | Only the intended resource is polled and caller cancellation remains respected. |
| Budget | Deadline, max polls, rate limit, or caller cancellation. |
| Stop Condition | Status is in the success terminal set. |
| Failure Condition | Status is in the failure terminal set, deadline expires, status fetch becomes unsafe, or caller cancels. |
| Recovery | Retry transient status fetch failures with bounded delay and preserve the last useful status. |
| Evidence | Final status, poll count, elapsed time, resource id, and stop reason. |

Red flags:

- Sleep in a loop with no deadline
- Only checks for success status
- No handling for failed, cancelled, expired, or unknown states
- No cancellation path
- Fixed aggressive interval against shared services

Verification:

- Every terminal state is handled.
- Tests cover success, failure terminal state, timeout, transient status fetch error, and cancellation or fake sleeper behavior.

Tests:

- Returns on success terminal state
- Raises or returns failure on failure terminal state
- Stops on deadline or max polls
- Uses fake clock or injectable sleeper
- Propagates cancellation

Failure modes:

- Infinite wait
- Stuck workflow
- Rate-limit pressure
- False success
- Uncancelable task

Related patterns:

- retry-loop
- durable-workflow-loop
- benchmark-loop

### LR-003 - Async Fan-Out Loop

Run many independent async operations without unbounded task creation or unclear partial failures.

Category: `concurrency`

Use when:

Use when processing many I/O-bound items concurrently with async tasks, promises, queues, or worker pools.

Prompt:

```text
Review or refactor this async fan-out loop with bounded concurrency, explicit partial-failure behavior, cancellation propagation, cleanup, and tests that prove max active work never exceeds the limit.
```

Contract:

| Element | Answer |
|---|---|
| Objective | Process every input item with bounded concurrency and produce terminal results. |
| State | Pending input, active tasks, completed results, failed results, cancellation state. |
| Action | Process one item under the concurrency limiter. |
| Progress | Completed plus failed count increases toward total input count. |
| Invariant | Active work never exceeds the configured capacity. |
| Budget | Concurrency limit, queue size, deadline, memory, downstream rate limit, or caller cancellation. |
| Stop Condition | Every input item has a terminal result or the caller cancels. |
| Failure Condition | Fatal configuration error, cancellation, or failure policy threshold exceeded. |
| Recovery | Record per-item failures, dead-letter where appropriate, and cancel siblings only for fatal errors. |
| Evidence | Result counts, failure records, max observed concurrency, and cancellation test output. |

Red flags:

- asyncio.gather over a huge mapped input
- Promise.all over unbounded input
- No semaphore, queue, worker pool, or capacity limiter
- Swallowed cancellation
- Implicit partial-failure policy

Verification:

- Concurrency and partial failures are controlled.
- Tests cover zero input, maximum concurrency, partial failure, fatal failure behavior, cancellation, and result aggregation.

Tests:

- Zero input returns quickly
- Max active workers never exceeds limit
- Individual failures are represented or escalated as designed
- Cancellation propagates and cleans up
- Result ordering is documented or tested when required

Failure modes:

- Socket exhaustion
- Memory spike
- Downstream overload
- Leaked tasks
- Lost item-level errors

Related patterns:

- distributed-backfill-loop
- polling-loop
- retry-loop

### LR-004 - Distributed Backfill Loop

Process large historical datasets with checkpoints, reconciliation, and safe resume behavior.

Category: `data`

Use when:

Use for migrations, crawlers, ETL jobs, reprocessing, and large backfills that can span deploys or failures.

Prompt:

```text
Design or audit this backfill loop with checkpointing, dedupe, idempotent writes, rate limits, dead-letter handling, resume behavior, reconciliation, and an evidence artifact.
```

Contract:

| Element | Answer |
|---|---|
| Objective | Process every eligible item exactly once or assign it to a terminal exception state. |
| State | Cursor, checkpoint, processed ids, failed ids, output version, rate-limit state. |
| Action | Read a bounded batch, process items, write outputs, and checkpoint progress. |
| Progress | Checkpoint advances and terminal item count increases. |
| Invariant | No item is written twice for the same output version. |
| Budget | Batch size, runtime window, rate limit, retry budget, cost cap, or daily quota. |
| Stop Condition | All eligible items are written, skipped, or dead-lettered. |
| Failure Condition | Checkpoint corruption, high error rate, quota exhaustion, schema mismatch, or reconciliation failure. |
| Recovery | Resume from verified checkpoint, skip already-terminal ids, and dead-letter repeated failures. |
| Evidence | Input/output counts, reconciliation report, checksum or sample audit, and dead-letter report. |

Red flags:

- No checkpoint or resume story
- Writes are not idempotent
- No reconciliation between source and output
- No dead-letter policy
- No rate-limit or cost budget

Verification:

- Backfill completion is reconciled.
- Evidence includes source count, output count, skipped count, failed count, checkpoint history, and replay or resume test.

Tests:

- Processes empty input
- Resumes after interruption without duplicate writes
- Dead-letters repeated item failures
- Honors batch and rate limits
- Produces reconciliation artifact

Failure modes:

- Duplicate output
- Silent data loss
- Unbounded runtime
- Quota burn
- Unrecoverable partial migration

Related patterns:

- async-fanout-loop
- retry-loop
- durable-workflow-loop

### LR-005 - ML Tuning Loop

Optimize model or hyperparameter choices without unbounded search or unverifiable improvement claims.

Category: `ml`

Use when:

Use for model training, hyperparameter tuning, prompt tuning, ranking optimization, or experiment search.

Prompt:

```text
Design or review this tuning loop with objective metric, baseline, validation split, budget, pruning or early stopping, failed-trial handling, reproducibility controls, and a final comparison artifact.
```

Contract:

| Element | Answer |
|---|---|
| Objective | Improve a named metric subject to explicit constraints. |
| State | Trial number, parameters, metrics, best score, failed trials, random seed, data version. |
| Action | Train, evaluate, and record one candidate. |
| Progress | Trial budget decreases and best valid metric may improve. |
| Invariant | Metric, validation split, data version, and acceptance constraints remain stable. |
| Budget | Trial count, wall-clock deadline, compute budget, max epochs, or early-stopping rule. |
| Stop Condition | Budget exhausted, target reached, or no-progress stop triggers. |
| Failure Condition | Non-finite metric, invalid config, repeated infrastructure failure, or acceptance constraint violation. |
| Recovery | Mark failed trials, prune unpromising runs, and preserve comparable metrics. |
| Evidence | Baseline, best result, constraints, trial table, best params, seed, and validation split id. |

Red flags:

- No baseline
- No validation split or data version
- No trial or time budget
- Accepting against the same signal used to optimize when overfitting is possible
- Only printing best params

Verification:

- Improvement is measured against a stable baseline.
- Final evidence compares baseline and selected candidate on the same acceptance criteria and records all budgets used.

Tests:

- Baseline metric recorded
- Trial or time budget enforced
- Failed trial handled
- Best result saved with params
- Acceptance constraint checked

Failure modes:

- Metric overfitting
- Runaway compute cost
- False improvement
- Irreproducible result
- Hidden failed trials

Related patterns:

- benchmark-loop
- agent-repair-loop

### LR-006 - Agent Repair Loop

Let a coding agent inspect, edit, and test without repeating the same failed action forever.

Category: `agent`

Use when:

Use when an agent is fixing tests, repairing CI, improving code, or iterating over implementation attempts.

Prompt:

```text
Define this agent repair loop with a cycle budget, current hypothesis, one focused edit per pass, deterministic check, repeated-failure detection, preservation of unrelated work, and completion evidence.
```

Contract:

| Element | Answer |
|---|---|
| Objective | Make the named check pass without changing unrelated behavior. |
| State | Hypothesis, inspected files, edited files, command output, repeated-failure count, remaining budget. |
| Action | Inspect, make one focused edit, and run the relevant deterministic check. |
| Progress | Failure changes, failing count decreases, or a hypothesis is falsified. |
| Invariant | Preserve unrelated user changes and keep edits scoped to implicated behavior. |
| Budget | Edit-test cycles, wall-clock time, commands, tokens, or user-defined cost. |
| Stop Condition | Target check and adjacent checks pass. |
| Failure Condition | Same failure repeats without changed hypothesis, budget is exhausted, or requirement is ambiguous. |
| Recovery | Change hypothesis, narrow the check, inspect fresh state, or ask for user input when blocked. |
| Evidence | Passing command output, changed file list, cycles used, and concise fix explanation. |

Red flags:

- Keep editing until it passes
- No repeated-failure stop
- No deterministic check
- Broad unrelated edits
- Claiming completion without command output

Verification:

- Agent completion is proven by deterministic checks.
- The final answer names the exact passing command, changed files, cycle count, and any residual risk.

Tests:

- Reproduces the target failure
- Passes the target check
- Runs adjacent check when relevant
- Stops on repeated identical failure
- Reports budget use

Failure modes:

- Infinite edit churn
- Unrelated regression
- Stale diagnosis
- False completion
- User changes overwritten

Related patterns:

- benchmark-loop
- ml-tuning-loop

### LR-007 - Benchmark Loop

Run experiments until evidence is useful or budget is exhausted, not until optimism wins.

Category: `evaluation`

Use when:

Use for agent evals, prompt comparisons, regression benchmarks, performance tuning, and research sweeps.

Prompt:

```text
Design or review this benchmark loop with fixed dataset and versions, objective metrics, sampling plan, budget, failure handling, separation between tuning signal and acceptance evidence, and reproducible artifacts.
```

Contract:

| Element | Answer |
|---|---|
| Objective | Measure or improve a named metric over a fixed evaluation scope. |
| State | Candidate, dataset version, run id, metric results, cost, failures, random seed. |
| Action | Run one candidate or experiment under recorded conditions. |
| Progress | Results table grows and uncertainty or candidate set shrinks. |
| Invariant | Evaluation scope, metric definition, and recording format remain stable. |
| Budget | Max runs, max spend, max wall-clock time, or statistical stopping rule. |
| Stop Condition | Target confidence reached, regression identified, candidate selected, or budget exhausted. |
| Failure Condition | Flaky infrastructure threshold exceeded, dataset invalid, or metric becomes non-comparable. |
| Recovery | Mark failed runs, rerun only under documented flake policy, and preserve raw outputs. |
| Evidence | CSV or JSON results, summary table, reproduction command, budget used, and final decision. |

Red flags:

- Try more prompts without a budget
- Changing dataset during comparison
- No raw result artifact
- Optimizing and accepting on the same small sample
- Ignoring failed or flaky runs

Verification:

- Benchmark result is reproducible and budgeted.
- Artifacts include fixed input versions, raw results, summary, reproduction command, and final decision rule.

Tests:

- Validates dataset manifest
- Records each run result
- Stops at max budget
- Handles flaky run policy
- Writes reproducible summary artifact

Failure modes:

- P-hacking
- Runaway spend
- Non-comparable results
- Lost raw evidence
- False winner

Related patterns:

- ml-tuning-loop
- agent-repair-loop
- polling-loop

### LR-008 - Durable Workflow Loop

Review long-running workflows for replay safety, idempotency, compensation, and terminal evidence.

Category: `workflow`

Use when:

Use for workflow engines, order fulfillment, approvals, sagas, scheduled jobs, and crash-resumable processes.

Prompt:

```text
Audit this durable workflow loop for idempotent steps, retry and compensation boundaries, replay safety, timeout behavior, human approval states, and terminal evidence.
```

Contract:

| Element | Answer |
|---|---|
| Objective | Move a business process from start to a terminal state without repeating unsafe side effects. |
| State | Workflow id, step state, external side-effect ids, retry state, compensation state, approval state. |
| Action | Advance one workflow step or compensation step. |
| Progress | Workflow step state advances toward a terminal outcome. |
| Invariant | Replay never repeats non-idempotent side effects. |
| Budget | Step timeouts, retry limits, approval deadlines, compensation budgets, or workflow lifetime. |
| Stop Condition | Workflow is fulfilled, cancelled, refunded, failed, or sent to manual review. |
| Failure Condition | Unsafe replay, compensation failure, external terminal failure, approval timeout, or inconsistent state. |
| Recovery | Use durable runtime state, idempotency keys, compensation steps, and manual-review handoff. |
| Evidence | Terminal state, step history, external ids, compensation records, and audit log. |

Red flags:

- Non-idempotent payment or message send inside replayable code
- Retrying compensation forever
- No human approval timeout
- No terminal failed or manual-review state
- Workflow persistence reimplemented ad hoc

Verification:

- Replay and terminal states are safe.
- Tests or review evidence show idempotency keys, compensation boundaries, timeouts, and terminal audit records.

Tests:

- Replay does not duplicate side effects
- Retry budget is enforced
- Compensation path is terminal
- Approval timeout is handled
- Audit log contains final state

Failure modes:

- Duplicate charge
- Stuck workflow
- Unbounded compensation
- Lost approval state
- Ad hoc persistence bug

Related patterns:

- retry-loop
- polling-loop
- distributed-backfill-loop
