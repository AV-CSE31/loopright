# Async Processing Contract

| Element | Answer |
|---|---|
| Objective | Process every queued item with bounded concurrency and produce a result for each input. |
| State | Pending items, active tasks, completed results, failed results. |
| Action | Run the item processor in a task group. |
| Progress | Completed plus failed count increases until it equals input count. |
| Invariant | Active tasks never exceed configured concurrency. |
| Budget | Maximum concurrency of 8 and a caller-provided cancellation signal. |
| Stop condition | All input items have terminal results. |
| Failure condition | Processor crash, cancellation, or unrecoverable item error. |
| Recovery | Mark item failed, cancel siblings only for fatal errors. |
| Evidence | Return result summary with counts and failure details. |

