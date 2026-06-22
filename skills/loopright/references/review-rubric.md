# Review Rubric

Use this rubric when reviewing loop-related code.

## Severity

| Severity | Meaning |
|---|---|
| P0 | Can hang indefinitely, corrupt data, overload a service, or cause runaway cost. |
| P1 | Likely failure in normal use: missing retry bounds, unsafe cancellation, duplicate side effects. |
| P2 | Important maintainability or observability gap: unclear progress, weak tests, vague stop reason. |
| P3 | Polish or clarity improvement. |

## Checklist

- Is the loop objective measurable?
- Is mutable state explicit?
- Is there a hard termination boundary?
- Can failure stop safely?
- Are retries limited to transient failures?
- Is polling respectful of rate limits and cancellation?
- Is concurrency bounded?
- Does the loop preserve required invariants?
- Are edge cases tested: zero input, one item, max budget, timeout, failure, cancellation?
- Is completion backed by evidence?

## Missing Evidence Patterns

Flag these as incomplete:

- "Looks good" without running or naming the relevant check.
- "Should converge" without metric history, threshold, or budget.
- "Retries safely" without a transient-failure allowlist and idempotency story.
- "Handles cancellation" without a test, framework primitive, or cleanup path.
- "Optimized" without a baseline and comparison.

## Minimum Test Matrix

| Loop type | Required tests |
|---|---|
| Retry | succeeds first try, retries transient failure, stops at budget, does not retry permanent failure |
| Polling | terminal success, terminal failure, timeout, cancellation or fake sleeper |
| Async concurrency | zero input, max concurrency, partial failure, cancellation |
| Batch processing | empty batch, partial failure, resume or dedupe behavior |
| ML tuning | baseline recorded, budget enforced, failed trial handled, best result saved |
| Agent repair | repeated failure detection, budget exhaustion, completion evidence |

## Review Output

Lead with bugs and risks. Cite the exact loop, condition, or missing test. Recommend the smallest correction that fits the codebase.
