# Retry Loop Contract

| Element | Answer |
|---|---|
| Objective | Upload a batch item once, retrying transient service failures until success or budget exhaustion. |
| State | Attempt count, current delay, last exception, item status. |
| Action | Call the upload API with an idempotency key. |
| Progress | Either the item reaches uploaded status or the attempt count advances with diagnostics. |
| Invariant | The same item id and idempotency key are used for every attempt. |
| Budget | At most 4 attempts or 30 seconds, whichever comes first. |
| Stop condition | API returns success or a known terminal duplicate-success status. |
| Failure condition | Non-transient error, budget exhaustion, cancellation, or invalid payload. |
| Recovery | Increase delay with jitter after transient failures; preserve final error context. |
| Evidence | Log final status, attempts used, elapsed time, and idempotency key. |

