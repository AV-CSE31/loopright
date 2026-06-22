# Example Task: ML Tuning Loop

## User Prompt

Use `$loopright` to design an Optuna loop for tuning a classifier.

## Risky Starting Point

```python
study.optimize(objective)
print(study.best_params)
```

## LoopRight Classification

ML hyperparameter-tuning loop.

## Findings

- **P1:** No trial count or timeout means the optimization budget is undefined.
- **P1:** No baseline metric makes improvement impossible to verify.
- **P2:** No pruning policy, failed-trial handling, validation split, seed, or final report is specified.
- **P2:** Printing `best_params` is not completion evidence.

## Loop Contract

| Element | Answer |
|---|---|
| Objective | Improve validation macro F1 over the current baseline. |
| State | Trial number, sampled parameters, validation score, best score, failed trials. |
| Action | Train and evaluate one model configuration. |
| Progress | Trial budget decreases and best validation macro F1 may improve. |
| Invariant | Same training data, validation split, objective metric, and seed policy across trials. |
| Budget | 50 trials or 2 hours, whichever comes first. |
| Stop condition | Trial or time budget is exhausted. |
| Failure condition | Non-finite metric, invalid config, repeated infrastructure failures. |
| Recovery | Mark failed trial, prune unpromising trials, stop if failure rate exceeds threshold. |
| Evidence | Save baseline score, best score, best params, trial table, seed, and validation split id. |

## Recommended Shape

```python
study = optuna.create_study(
    direction="maximize",
    pruner=optuna.pruners.MedianPruner(n_warmup_steps=5),
)
study.optimize(objective, n_trials=50, timeout=7200, catch=(RecoverableTrialError,))

report = {
    "baseline_macro_f1": baseline_score,
    "best_macro_f1": study.best_value,
    "best_params": study.best_params,
    "trials": len(study.trials),
    "validation_split": validation_split_id,
    "seed": seed,
}
save_json(report, "tuning-report.json")
```

## Evidence

- Baseline score is recorded before tuning.
- Trial budget is enforced.
- Failed trials are tracked.
- Best result is compared against baseline.
- Report artifact is saved and named in the final answer.

