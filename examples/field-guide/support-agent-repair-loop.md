# Support Agent Repair Loop

## User Prompt

```text
$loopright Create a repair loop for a coding agent that fixes failing Zendesk sync tests.
The agent can edit code and run tests, but it must stop before it churns on the same failure.
```

## Risky Starting Point

```text
Keep changing the code until the tests pass. If a test still fails, inspect the code,
try another fix, and keep going.
```

## LoopRight Diagnosis

Verdict: Repair needed

Findings:

- P1: No cycle budget or wall-clock budget.
- P1: No repeated-failure stop when the same error persists.
- P2: The prompt does not require a hypothesis before editing.
- P2: Completion can be claimed without the exact passing command output.
- P2: No rule protects unrelated user changes.

## Loop Contract

| Element | Answer |
|---|---|
| Objective | Fix the failing Zendesk sync tests while preserving unrelated changes and producing deterministic test evidence. |
| State | Current failure signature, hypothesis, files inspected, files edited, command run, cycle count, repeated failure count. |
| Action | Reproduce failure, form hypothesis, make one focused edit, run the narrow test, compare failure signature, decide continue or stop. |
| Progress | Failure signature changes, failing test count decreases, or target command passes. |
| Invariant | Do not revert unrelated user changes and do not edit files outside the sync boundary without naming why. |
| Budget | Max 6 repair cycles, max 45 minutes, max 2 repeats of the same failure signature without a changed hypothesis. |
| Stop condition | Target command passes, budget exhausts, same failure repeats without a new hypothesis, or requirement ambiguity blocks progress. |
| Failure condition | Cannot reproduce failure, fixture behavior is ambiguous, same failure repeats three times, or edits expand beyond allowed boundary. |
| Recovery | Revert only the agent's last focused edit if it worsens the failure, summarize hypothesis history, ask for clarification when blocked. |
| Evidence | Final command output, cycle log, changed-file list, and repeated-failure guard status. |

## Minimal Repair

```text
Cycle 0: reproduce once.
For cycles 1..6:
  1. Write one hypothesis.
  2. Edit the smallest relevant code path.
  3. Run the narrow deterministic command.
  4. Compare the failure signature.
  5. Stop if the same signature repeats without a new hypothesis.
Finish only with exact command output and changed-file list.
```

Example evidence:

```text
Command: pytest tests/integrations/test_zendesk_sync.py::test_retries_429_once -q
Result: 1 passed
Cycles used: 3/6
Changed files: zendesk/sync.py, tests/integrations/test_zendesk_sync.py
Repeated-failure guard: not triggered
```

## Required Evidence

- The first cycle records the original failure signature.
- Every edit is paired with a hypothesis.
- The final response includes the exact passing command.
- If the agent stops blocked, it includes the repeated failure signature and what changed between attempts.
