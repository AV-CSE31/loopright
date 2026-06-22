# Example Task: Retry Upload Review

## User Prompt

Use `$loopright` to review and fix this retry loop:

```python
def upload_forever(client, payload):
    while True:
        try:
            return client.upload(payload)
        except Exception:
            time.sleep(1)
```

## LoopRight Classification

Retry loop.

## Findings

- **P0:** `while True` can run forever because there is no max attempt count, deadline, or cancellation path.
- **P1:** `except Exception` retries validation, auth, programming, and corrupt-payload failures that should stop immediately.
- **P1:** The upload may duplicate external side effects because the loop has no idempotency key or deduplication contract.
- **P2:** The function returns no evidence about attempts, elapsed time, or stop reason.

## Loop Contract

| Element | Answer |
|---|---|
| Objective | Upload one payload exactly once or fail with a clear terminal reason. |
| State | Attempt count, elapsed time, last transient error, idempotency key. |
| Action | Call `client.upload(payload, idempotency_key=key)`. |
| Progress | Attempt count increases and either upload succeeds or a terminal failure is identified. |
| Invariant | Every attempt uses the same payload and idempotency key. |
| Budget | At most 4 attempts or 30 seconds. |
| Stop condition | Upload returns success or duplicate-success status. |
| Failure condition | Non-transient error, invalid payload, auth failure, cancellation, or exhausted budget. |
| Recovery | Retry only transient network/rate-limit failures with jittered exponential backoff. |
| Evidence | Return upload result plus attempts used, elapsed time, and stop reason in logs or metadata. |

## Recommended Shape

```python
def upload_with_retry(client, payload, *, idempotency_key, max_attempts=4, sleep=time.sleep):
    delay = 0.5
    for attempt in range(1, max_attempts + 1):
        try:
            result = client.upload(payload, idempotency_key=idempotency_key)
            logger.info("upload complete", extra={"attempt": attempt})
            return result
        except (TimeoutError, RateLimitError) as exc:
            if attempt == max_attempts:
                raise UploadFailed("upload retry budget exhausted") from exc
            sleep(delay + random.uniform(0, delay / 4))
            delay = min(delay * 2, 8)
```

## Evidence

- Unit test succeeds on first attempt.
- Unit test retries transient failures and then succeeds.
- Unit test stops after `max_attempts`.
- Unit test does not retry validation/auth errors.
- Log includes attempts and terminal stop reason.

