# Loop Patterns

## Contract-First Design

Start every non-trivial loop by naming the objective, mutable state, action, progress signal, invariant, budget, stop condition, failure condition, recovery path, and evidence.

Good loops make forward movement visible. Bad loops hide state, rely on hope, and make failure look like patience.

## Common Loop Types

| Type | Use when | Watch for |
|---|---|---|
| Finite collection | Input is known and bounded | Mutation during iteration, hidden side effects |
| Condition-controlled | Stop depends on changing state | Missing hard budget, stale state |
| Batch processing | Work is split into chunks | Partial failure, duplicate processing |
| Optimization | Search improves a metric | No baseline, no budget, overfitting |
| Repair loop | Attempts fix and verification | Repeating the same failed action |
| Durable loop | Work spans crashes or approvals | Reimplementing persistence or scheduling |

## Termination Boundaries

Every loop needs at least one hard boundary:

- Maximum iterations
- Deadline
- Cancellation signal
- Input exhaustion
- Resource budget
- Convergence threshold
- Explicit terminal state

Soft convergence is helpful but insufficient when floating point noise, network state, or model variance can prevent equality.

## Evidence Examples

- Passing tests that cover edge cases and termination.
- Logged final state with iteration count and stop reason.
- Metric table showing baseline, best value, and budget used.
- Output artifact with checksum, row count, or validation report.
- Review note explaining why the selected primitive is sufficient.

