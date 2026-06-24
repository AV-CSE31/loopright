# Realtime Enrichment Fan-Out

## User Prompt

```text
$loopright Refactor this Node service. It receives up to 20k signup events per minute,
calls three enrichment vendors, and writes profile traits. During launches it overwhelms
the fraud vendor and starts timing out.
```

## Risky Starting Point

```typescript
await Promise.all(events.map(async event => {
  const fraud = await fraudApi.score(event.email)
  const crm = await crmApi.lookup(event.company)
  const geo = await geoApi.lookup(event.ip)
  await profiles.write(event.userId, { fraud, crm, geo })
}))
```

## LoopRight Diagnosis

Verdict: Repair needed

Findings:

- P1: `Promise.all` creates work proportional to input size with no capacity limit.
- P1: One vendor timeout can reject the full batch and lose partial progress.
- P2: Vendor-specific budgets are missing even though each downstream service has different limits.
- P2: No dead-letter or replay key is defined for partial enrichment failures.

## Loop Contract

| Element | Answer |
|---|---|
| Objective | Enrich each signup event at most once per enrichment version and write available traits without exceeding vendor capacity. |
| State | Input offset, event id, vendor budgets, in-flight counts, per-vendor result, profile write status, dead-letter records. |
| Action | Pull a bounded batch, process with worker pool, call vendors through per-vendor limiters, write idempotent profile update, record terminal outcome. |
| Progress | Input offset advances and terminal event count increases. |
| Invariant | Profile writes use `(event_id, enrichment_version)` as the idempotency key. |
| Budget | Worker concurrency 64, fraud vendor concurrency 12, CRM concurrency 24, geo concurrency 48, event timeout 8 seconds, max 2 transient attempts per vendor. |
| Stop condition | Batch input exhausted and every event is terminal: enriched, partially enriched, skipped duplicate, or dead-lettered. |
| Failure condition | Queue lag above alert threshold, vendor error rate above budget, profile store unavailable, or timeout budget exhausted. |
| Recovery | Resume from committed offset, skip idempotent writes, replay dead letters after vendor recovery, degrade non-critical traits when policy allows. |
| Evidence | Metrics for queue lag, in-flight counts, vendor attempts, partial-enrichment counts, dead-letter count, and duplicate-write count. |

## Minimal Repair

Use two levels of control:

```text
event worker pool
  -> fraud limiter, retry only transient 429/503
  -> CRM limiter, timeout and partial trait result
  -> geo limiter, timeout and partial trait result
  -> idempotent profile write
  -> terminal event record
```

The repair is not "wrap `Promise.all` in try/catch." It changes the loop contract so each event can finish with an auditable terminal result.

## Required Evidence

- Load test: 10k synthetic events with max active event workers at or below 64.
- Vendor metrics: fraud in-flight never exceeds 12.
- Partial failure test: CRM timeout records partial result and still writes permitted traits.
- Replay test: same event id and enrichment version does not duplicate profile writes.
