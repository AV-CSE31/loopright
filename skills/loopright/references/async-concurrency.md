# Async and Concurrency

## Design Rules

- Prefer structured concurrency: task groups, nurseries, or framework-native equivalents.
- Bound parallelism with a semaphore, capacity limiter, worker pool, or queue.
- Propagate cancellation instead of swallowing it.
- Make cleanup idempotent.
- Avoid unbounded task creation from unbounded input.
- Preserve result ordering only when callers require it.

## Failure Handling

Decide whether one worker failure should:

- Cancel all work.
- Mark only that item failed.
- Retry the item.
- Defer the item to a dead-letter path.

Do not leave this behavior implicit.

## Tests

Test cancellation, timeout, partial failure, zero input, maximum concurrency, and result aggregation. For timing-sensitive code, prefer fake clocks or injectable sleepers.

