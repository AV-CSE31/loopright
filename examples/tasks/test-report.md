# LoopRight Example Task Test Report

Date: 2026-06-22

## Summary

The example task suite exercises the skill across five loop categories:

- Retry upload review
- Job polling design
- Async batch processor
- ML tuning loop
- Agent repair loop

## Results

| Task | Contract complete | Risk findings present | Evidence specified |
|---|---:|---:|---:|
| Retry upload review | Yes | Yes | Yes |
| Job polling design | Yes | Yes | Yes |
| Async batch processor | Yes | Yes | Yes |
| ML tuning loop | Yes | Yes | Yes |
| Agent repair loop | Yes | Yes | Yes |

## Observations

- The skill consistently forces a loop contract before implementation.
- The review rubric helps prioritize unbounded loops and unsafe retries as high-severity issues.
- The examples show that LoopRight is useful as both an implementation guide and a review checklist.
- The validator catches missing contract fields, but deeper correctness still depends on tests and code review.

## Follow-Up Ideas

- Add runnable Python tests for the retry and polling examples.
- Add a CI job that validates every Markdown contract in `examples/`.
- Add one TypeScript example for frontend or Node.js developers.
