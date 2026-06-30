# Agent and Iterative Repair Loops

## Agent Loop Contract

Agent loops must make these policies explicit:

- Allowed actions and tools.
- Automation trigger, cadence, and maximum runtime.
- Durable state store and what fields the agent may update.
- Maker-checker split when the loop proposes consequential actions.
- State that changes between turns.
- Progress signal.
- Repeated-failure detection.
- Budget for turns, tokens, time, commands, or money.
- Stop condition.
- Escalation or user-input condition.
- Connector side-effect boundary, idempotency, and dry-run behavior.
- Kill switch or risk-monitor condition for high-impact loops.
- Memory-update governance: what can become a future rule and who approves it.
- Completion evidence.

## Repeated Failure

If the same failure repeats, change the plan or stop. A useful loop records the failed action, observed result, hypothesis, and next different action.

## Tool Use

Do not use an LLM to decide facts that a deterministic command can verify. Use tests, linters, type checkers, logs, database queries, or API responses as evidence.

For consequential actions, the agent that proposes the action should not be the only verifier. Use a separate checker, deterministic metric, approval gate, or stronger review path before side effects run.

## Connectors and Side Effects

Connector-backed loops can affect real systems. Require dry-run mode, explicit permission boundaries, idempotency keys or compensation, rate limits, and audit records. Treat broker, deploy, database, payment, messaging, and ticketing connectors as side-effecting tools even when the agent describes the action as "just a test."

## State and Memory

State files preserve continuity; they also preserve mistakes. Record trigger ids, state snapshots, decisions, verifier verdicts, side-effect ids, and stop reasons. Queue lessons or memory updates for review before they become future rules, especially when the lesson comes from one failed run or one loss event.

## Kill Switches

High-impact agent loops need a separate stop path. A risk monitor should stop or freeze the loop when budgets, permissions, stale-state checks, drawdown/exposure limits, or connector-health checks fail.

## Completion

Completion requires objective evidence: passing checks, changed files, benchmark numbers, deployment status, rendered artifacts, or a clear explanation of why no code change was needed.
