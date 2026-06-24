# Test Coverage Sweep

## User Prompt

```text
$loopright Set up a loop that gets our payments service to 100% test coverage.
Keep generating tests and running coverage until we hit 100%, then stop.
```

## Risky Starting Point

```python
while True:
    cov = measure_coverage()          # agent's own estimate, not the tool
    if cov >= 100:
        break
    write_more_tests()                # any file, any assertion
```

## LoopRight Diagnosis

Verdict: Unsafe to run

Findings:

- P1: Unbounded sweep with no pass budget, cost cap, or diminishing-returns stop.
- P1: Coverage is self-reported by the agent instead of read from the coverage tool, so completion can be falsely claimed.
- P1: No no-gaming invariant, so the target is reachable with assertion-free tests or `# pragma: no cover` exclusions.
- P2: Unrelated behavior and the existing passing suite are not protected against regression.
- P2: No evidence artifact records before/after coverage, skipped lines, or budget used.

## Loop Contract

| Element | Answer |
|---|---|
| Objective | Raise `coverage.py` branch coverage of `payments/` from baseline toward the target, or stop at a documented point, without breaking the existing suite. |
| State | Baseline report, current coverage, target, remaining uncovered worklist, lines closed this pass, consecutive no-progress passes, remaining pass budget. |
| Action | Read the coverage report, pick the highest-value uncovered branch, add one scoped test, and re-run coverage. |
| Progress | Tool-measured branch coverage rises or the uncovered worklist shrinks. |
| Invariant | Coverage is read from `coverage.py`, not estimated; new tests assert real behavior; no `no cover` pragmas or file exclusions are added; unrelated code stays unchanged. |
| Budget | Max 12 passes, 2 consecutive no-progress passes, and a wall-clock deadline. |
| Stop condition | Target reached and re-verified, 2 consecutive passes add no covered lines, or the pass budget is exhausted. |
| Failure condition | Coverage regresses, the existing suite fails, the coverage tool errors, or a branch is unreachable without gaming. |
| Recovery | Revert the last test on regression, re-baseline from the tool, and dead-letter genuinely unreachable branches for human review. |
| Evidence | Before/after coverage JSON from `coverage.py`, list of branches dead-lettered as unreachable, passes used, and a green run of the full suite. |

## Minimal Repair

```python
target = 100.0
no_progress = 0
baseline = run_coverage("payments/")        # independent tool, not the agent
best = baseline.percent

for pass_no in range(1, 13):
    gap = baseline.highest_value_uncovered()
    if gap is None:
        stop("worklist-empty", pass_no); break

    add_one_assertive_test(gap)
    report = run_coverage("payments/")
    if not report.suite_passed or report.percent < best:
        revert_last_test(); stop("regression", pass_no); break

    gained = report.percent - best
    best = report.percent
    no_progress = 0 if gained > 0 else no_progress + 1

    if best >= target:
        stop("target-reached", pass_no); break
    if no_progress >= 2:
        stop("diminishing-returns", pass_no); break
else:
    stop("pass-budget-exhausted", 12)
```

## Required Evidence

- `coverage.py` JSON for `payments/` before and after, showing the measured delta.
- Full payments suite passes green on the final pass.
- Branches reported as unreachable are dead-lettered with reasons, not pragma-excluded.
- Stop reason recorded: `target-reached`, `diminishing-returns`, `regression`, or `pass-budget-exhausted`.
