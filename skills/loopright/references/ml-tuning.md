# ML Training and Tuning Loops

## Required Contract

Name the optimization target, baseline, validation data, budget, pruning rule, reproducibility controls, and final selection evidence.

## Training Loops

Require:

- Epoch or step budget.
- Validation cadence.
- Early stopping or explicit reason not to use it.
- Checkpoint policy.
- Metric logging.
- Seed and configuration capture when reproducibility matters.

## Hyperparameter Tuning

Prefer established optimizers and experiment tracking already used by the project.

Require:

- Search space.
- Objective metric and direction.
- Trial budget or deadline.
- Pruning or stop policy.
- Handling for failed trials.
- Final comparison against baseline.

Do not call a tuning loop optimal unless an optimization criterion and evidence are stated.

