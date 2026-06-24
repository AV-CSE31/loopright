# LoopRight Case Studies

These are compact, reproducible stories that show where LoopRight changes the engineering outcome.

## Runaway Retry Cost

Scenario:

A file-upload worker retries every failed upload with `except Exception` and no attempt budget. During a partial provider outage, permanent validation errors are retried alongside transient network failures.

LoopRight diagnosis:

- Broad exception catch hides permanent failures.
- No retry budget or stop reason.
- No idempotency or duplicate-side-effect evidence.
- No final artifact proving which records uploaded, failed permanently, or exhausted retry budget.

Minimal repair:

- Retry only named transient exceptions.
- Add `max_attempts`, exponential backoff, jitter, and idempotency key.
- Stop permanent failures immediately.
- Return evidence with attempts, stop reason, and error classes.

Required evidence:

- Transient failure eventually succeeds within budget.
- Permanent failure is not retried.
- Retry budget exhaustion records a terminal result.
- Upload reconciliation report matches input count.

Runnable proof:

```bash
python -m unittest discover -s examples/runnable/python -p "test_retry_upload.py"
```

## Unbounded Async Fan-Out

Scenario:

An async pipeline reads a large event collection and calls `asyncio.gather` over the entire input. It passes small tests but overloads downstream services in production.

LoopRight diagnosis:

- Task creation is proportional to input size.
- No concurrency limit or downstream capacity contract.
- Partial failure behavior is undefined.
- Cancellation and cleanup evidence is missing.

Minimal repair:

- Replace unbounded fan-out with a fixed worker pool.
- Track active workers, successes, failures, and dead letters.
- Add timeout and cancellation behavior.
- Test max concurrency with synthetic input.

Required evidence:

- `max_active_workers` never exceeds the configured limit.
- Partial failures are dead-lettered without stopping unrelated work.
- Zero-input and timeout cases finish with explicit stop reasons.

Runnable proof:

```bash
python -m unittest discover -s examples/runnable/python -p "test_async_worker_pool.py"
```

## Coding-Agent Repair Churn

Scenario:

An agent prompt says: "Keep trying until it works." The agent edits the same files repeatedly, reruns broad tests, and reports progress without a new hypothesis or deterministic completion check.

LoopRight diagnosis:

- No cycle budget.
- No repeated-failure stop.
- No requirement to change hypothesis after a failed cycle.
- Success is subjective unless tied to a command, artifact, or metric.

Minimal repair:

- Limit the inspect-edit-test loop to a fixed number of cycles.
- Require one focused hypothesis and one focused edit per cycle.
- Stop after the same failure repeats without a changed hypothesis.
- Claim completion only with the exact passing command and changed-file list.

Required evidence:

- Reproduction command.
- Cycle count used versus budget.
- Hypothesis history.
- Final deterministic check output.
- Repeated-failure guard status.
