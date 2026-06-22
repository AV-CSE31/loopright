# Agent Loop Contract

| Element | Answer |
|---|---|
| Objective | Fix a failing test without changing unrelated behavior. |
| State | Hypothesis, edited files, command output, remaining budget. |
| Action | Inspect code, make a focused edit, run the relevant test. |
| Progress | Failing assertion changes, failing test count decreases, or a new diagnosis is proven. |
| Invariant | Do not revert user changes or edit unrelated modules. |
| Budget | 6 edit-test cycles. |
| Stop condition | Target test passes and related checks pass. |
| Failure condition | Same failure repeats three times without a new hypothesis, or budget is exhausted. |
| Recovery | Re-read code, shrink scope, ask for user input if the requirement is ambiguous. |
| Evidence | Passing test output and concise change summary. |

