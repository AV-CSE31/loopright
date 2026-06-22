# LoopRight Example Task Suite

These examples exercise the `loopright` skill on realistic agent prompts. Each task records:

- The prompt a user might give an agent.
- The risky starting point or scenario.
- The LoopRight contract.
- The recommended implementation or review result.
- The evidence expected before claiming completion.

## Tasks

| Task | Loop category | What LoopRight should catch |
|---|---|---|
| [Retry upload review](retry-upload-review.md) | Retry loop | Unbounded retry, broad exception catch, missing idempotency and evidence |
| [Job polling design](job-polling-design.md) | Polling loop | Missing deadline, no failure terminal states, no cancellation |
| [Async batch processor](async-batch-processor.md) | Async concurrency | Unbounded task creation, unclear partial failure policy |
| [ML tuning loop](ml-tuning-loop.md) | Hyperparameter tuning | No baseline, no budget, no pruning or final comparison |
| [Agent repair loop](agent-repair-loop.md) | Agent tool-use loop | Repeating the same failed action without changed hypothesis |

## How to Use

Use these as forward-test prompts when editing the skill:

```text
Use $loopright at skills/loopright to solve examples/tasks/retry-upload-review.md.
```

The output should define the loop contract before proposing code, identify risks by severity when reviewing code, and end with concrete completion evidence.

