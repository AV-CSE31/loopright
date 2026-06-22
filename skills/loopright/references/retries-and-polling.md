# Retries and Polling

## Retry Loops

Retry only when the failure is likely transient and the action is safe to repeat.

Require:

- A bounded attempt count or deadline.
- A narrow exception or status allowlist.
- Backoff, usually exponential.
- Jitter when many clients may retry together.
- Idempotency or deduplication when actions mutate external state.
- A final failure path that preserves the original error context.

Avoid:

- Retrying validation errors, permission errors, programmer errors, or corrupt data.
- Catching broad exceptions without re-raising unknown failures.
- Resetting useful diagnostics on each attempt.

## Polling Loops

Polling must include:

- A deadline or max polls.
- A delay policy.
- Cancellation support.
- A terminal status allowlist.
- A failure status allowlist.
- Clear evidence of final status.

Prefer callbacks, events, webhooks, queues, or runtime-native waiting primitives when available.

## Delay Policy

Use deterministic small sleeps only in tests or single-client local workflows. Use jittered backoff for shared external systems.

Document whether the delay is tuned for responsiveness, load shedding, fairness, or rate-limit compliance.

