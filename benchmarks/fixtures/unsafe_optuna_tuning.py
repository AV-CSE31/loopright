"""Optuna study with no trial or wall-clock budget in the optimize call."""

import optuna


def objective(trial):
    depth = trial.suggest_int("depth", 2, 12)
    rate = trial.suggest_float("rate", 1e-5, 1e-1, log=True)
    return train_and_score(depth, rate)


study = optuna.create_study(direction="maximize")
study.optimize(objective)
print(study.best_params)
