# CI Job Poller

## User Prompt

```text
$loopright Review this deploy gate. It polls Buildkite, waits for a canary job to finish,
and then promotes the release if the job passes.
```

## Risky Starting Point

```typescript
while (true) {
  const job = await buildkite.getJob(jobId)
  if (job.state === "passed") break
  await sleep(10000)
}
await promoteRelease(releaseId)
```

## LoopRight Diagnosis

Verdict: Unsafe to run

Findings:

- P1: Polling loop has no deadline, cancellation signal, or max poll count.
- P1: Failed, canceled, timed-out, and blocked states are not terminal, so promotion can hang forever.
- P2: Promotion is not tied to the exact job/build id that was checked.
- P2: No evidence artifact tells an incident reviewer why the deploy promoted or stopped.

## Loop Contract

| Element | Answer |
|---|---|
| Objective | Promote release `r-2026-06-24.3` only if canary job `bk-913728` reaches `passed` before the deploy deadline. |
| State | Poll count, elapsed time, last observed job state, build id, cancellation status, promotion decision. |
| Action | Fetch job status, classify terminal state, record observation, sleep with bounded interval, or promote only after verified pass. |
| Progress | Poll count increases and last observed state is recorded with timestamp. |
| Invariant | Promotion must reference the same build id and job id that were polled. |
| Budget | Max 90 polls, 15 minutes wall-clock deadline, 10 second interval, cancellation from deploy controller. |
| Stop condition | Job reaches `passed`, `failed`, `canceled`, `blocked`, `timed_out`, deadline expires, or cancellation is requested. |
| Failure condition | API authentication failure, job id changes, deadline exceeded, or terminal non-pass state. |
| Recovery | Abort promotion, write deploy-gate report, allow operator to rerun with a fresh job id. |
| Evidence | Deploy-gate JSON with release id, build id, job id, final state, polls used, elapsed time, and promotion decision. |

## Minimal Repair

```typescript
const terminal = new Set(["passed", "failed", "canceled", "blocked", "timed_out"])
const deadline = Date.now() + 15 * 60 * 1000

for (let poll = 1; poll <= 90; poll++) {
  if (abortSignal.aborted) return stop("cancelled", poll)
  const job = await buildkite.getJob(jobId)
  observations.push({ poll, state: job.state, buildId: job.buildId })
  if (job.buildId !== expectedBuildId) return stop("wrong-build", poll)
  if (job.state === "passed") return promoteRelease(releaseId, { jobId, buildId: job.buildId })
  if (terminal.has(job.state)) return stop(`terminal-${job.state}`, poll)
  if (Date.now() >= deadline) return stop("deadline-exceeded", poll)
  await sleep(10000)
}
return stop("poll-budget-exhausted", 90)
```

## Required Evidence

- Unit test: `failed`, `canceled`, `blocked`, and `timed_out` stop without promotion.
- Unit test: deadline exceeded records a stop reason.
- Unit test: job/build mismatch blocks promotion.
- Deploy log includes final state, polls used, elapsed time, and exact promotion decision.
