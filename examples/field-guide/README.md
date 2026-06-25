# LoopRight Field Guide

These examples are meant to look like real engineering work, not polished demo prompts. Each one includes a messy starting point, concrete operational pressure, a LoopRight contract, and the evidence a reviewer should require before accepting the loop.

Use these examples when you want to show why LoopRight matters:

| Example | Loop type | Why it feels real |
|---|---|---|
| [Billing webhook replay](billing-webhook-replay.md) | Retry and backfill | Replays vendor webhooks without double-charging or hiding permanent failures. |
| [Embedding backfill](embedding-backfill.md) | Distributed backfill | Handles model versioning, rate limits, checkpoints, and partial re-runs. |
| [CI job poller](ci-job-poller.md) | Polling | Polls external jobs with terminal states, cancellation, and incident evidence. |
| [Realtime enrichment fan-out](realtime-enrichment-fanout.md) | Async concurrency | Prevents `Promise.all` style overload while preserving partial-failure records. |
| [Support agent repair loop](support-agent-repair-loop.md) | Agent tool-use | Stops a coding agent from repeating failed fixes without a changed hypothesis. |
| [Autonomous quant research loop](autonomous-quant-research-loop.md) | Autonomous decision loop | Turns a self-improving trading-agent idea into a paper-trading loop with maker-checker verification, state governance, connector boundaries, and kill switches. |

## Quality Bar

A good LoopRight example should include:

- A believable user prompt.
- A risky starting point.
- A loop contract with objective, state, action, progress, invariant, budget, stop condition, failure condition, recovery, and evidence.
- Findings that name a specific failure mode.
- A minimal repair that preserves the intended business outcome.
- Evidence that could be checked by a reviewer, CI job, dashboard, or incident owner.
