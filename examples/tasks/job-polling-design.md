# Example Task: Job Polling Design

## User Prompt

Use `$loopright` to design a loop that waits for a remote export job to finish.

## Risky Starting Point

```python
while api.get_job(job_id)["status"] != "done":
    time.sleep(5)
```

## LoopRight Classification

Polling loop.

## Findings

- **P0:** The loop can wait forever if the job is stuck or the status endpoint degrades.
- **P1:** Failure terminal states such as `failed`, `cancelled`, or `expired` are not handled.
- **P1:** The loop has no cancellation or deadline, so callers cannot stop it cleanly.
- **P2:** The final result lacks evidence such as final status, polls used, and elapsed time.

## Loop Contract

| Element | Answer |
|---|---|
| Objective | Wait until a known job reaches a terminal status and return that status. |
| State | Current status, poll count, elapsed time, last response. |
| Action | Fetch job status from the API. |
| Progress | Poll count advances and status transitions are observed. |
| Invariant | Poll only the requested job id and preserve caller cancellation. |
| Budget | Deadline of 10 minutes or max 120 polls. |
| Stop condition | Status is `done`. |
| Failure condition | Status is `failed`, `cancelled`, `expired`, deadline exceeded, or caller cancellation. |
| Recovery | Retry transient status fetch errors with bounded backoff. |
| Evidence | Return final status, poll count, elapsed time, and job id. |

## Recommended Shape

Use a deadline, terminal status sets, cancellation support, and an injectable sleeper for tests.

```python
def wait_for_export(api, job_id, *, deadline_s=600, interval_s=5, monotonic=time.monotonic, sleep=time.sleep):
    started = monotonic()
    polls = 0
    while monotonic() - started < deadline_s:
        polls += 1
        status = api.get_job(job_id)["status"]
        if status == "done":
            return {"job_id": job_id, "status": status, "polls": polls, "elapsed_s": monotonic() - started}
        if status in {"failed", "cancelled", "expired"}:
            raise ExportFailed(f"job {job_id} ended with {status}")
        sleep(interval_s)
    raise TimeoutError(f"job {job_id} did not finish within {deadline_s}s after {polls} polls")
```

## Evidence

- Test `done` returns final status.
- Test failure terminal states raise immediately.
- Test deadline exhaustion raises timeout.
- Test uses fake clock/sleeper instead of real sleep.

