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

## Review Output

Lead with bugs and risks. Cite the exact loop, condition, or missing test. Recommend the smallest correction that fits the codebase.

