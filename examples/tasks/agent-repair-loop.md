# Example Task: Agent Repair Loop

## User Prompt

Use `$loopright` to define a safe coding-agent repair loop for fixing a failing test.

## Risky Starting Point

```text
Keep editing until the test passes.
```

## LoopRight Classification

Agent tool-use and iterative code-repair loop.

## Findings

- **P0:** The instruction is unbounded and may consume unlimited turns, commands, or tokens.
- **P1:** It does not detect repeated failure or require a changed hypothesis.
- **P1:** It does not protect unrelated user changes or unrelated files.
- **P2:** Completion evidence is vague.

## Loop Contract

| Element | Answer |
|---|---|
| Objective | Make the named failing test pass without changing unrelated behavior. |
| State | Current hypothesis, files read, files edited, command output, remaining budget. |
| Action | Inspect, edit narrowly, run the relevant deterministic check. |
| Progress | Failure changes, failing test count decreases, or a diagnosis is proven false. |
| Invariant | Preserve unrelated user changes and keep edits scoped to the implicated code. |
| Budget | 6 inspect-edit-test cycles or 45 minutes. |
| Stop condition | Target test and adjacent checks pass. |
| Failure condition | Same failure repeats 3 times without a new hypothesis, budget exhausted, or requirement is ambiguous. |
| Recovery | Re-read code, inspect narrower logs, reduce scope, or ask the user when blocked. |
| Evidence | Passing command output, changed file list, and concise explanation of the fix. |

## Recommended Agent Policy

1. Reproduce the failure once.
2. Identify the smallest implicated code path.
3. Make one focused edit.
4. Run the narrow test.
5. If the same failure repeats, record why and change the hypothesis before another edit.
6. Stop after budget exhaustion and report the best evidence gathered.

## Evidence

- The final response includes the exact passing command.
- The diff touches only relevant files.
- Repeated failures are not retried blindly.

