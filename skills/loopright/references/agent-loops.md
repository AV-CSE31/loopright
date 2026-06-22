# Agent and Iterative Repair Loops

## Agent Loop Contract

Agent loops must make these policies explicit:

- Allowed actions and tools.
- State that changes between turns.
- Progress signal.
- Repeated-failure detection.
- Budget for turns, tokens, time, commands, or money.
- Stop condition.
- Escalation or user-input condition.
- Completion evidence.

## Repeated Failure

If the same failure repeats, change the plan or stop. A useful loop records the failed action, observed result, hypothesis, and next different action.

## Tool Use

Do not use an LLM to decide facts that a deterministic command can verify. Use tests, linters, type checkers, logs, database queries, or API responses as evidence.

## Completion

Completion requires objective evidence: passing checks, changed files, benchmark numbers, deployment status, rendered artifacts, or a clear explanation of why no code change was needed.

