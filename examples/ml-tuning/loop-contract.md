# ML Tuning Contract

| Element | Answer |
|---|---|
| Objective | Improve validation F1 over the baseline model. |
| State | Trial parameters, validation score, best score, trial status. |
| Action | Train and evaluate one trial using the project training entry point. |
| Progress | Best validation F1 improves or the trial budget decreases. |
| Invariant | Every trial uses the same validation split and objective metric. |
| Budget | 40 trials or 2 hours. |
| Stop condition | Trial budget is exhausted or pruning stops unpromising trials. |
| Failure condition | Invalid configuration, non-finite metric, repeated infrastructure failure. |
| Recovery | Mark failed trial and continue unless failure rate exceeds threshold. |
| Evidence | Save best parameters, baseline score, best score, and trial table. |

