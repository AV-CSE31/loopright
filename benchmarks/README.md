# LoopRight Benchmarks

This benchmark suite measures deterministic scanner behavior over small unsafe and safe fixtures.

Run it:

```bash
python benchmarks/run_loopright_benchmark.py
```

Regenerate the published results table:

```bash
python benchmarks/run_loopright_benchmark.py --format md --output benchmarks/RESULTS.md
```

Current results live in [RESULTS.md](RESULTS.md). CI regenerates that file and fails if it
drifts, so the published numbers always match the rules in the repository.

The benchmark reports:

- expected versus observed high-confidence risks per fixture
- missing and unexpected findings
- overall precision and recall
- per-rule precision and recall
- which scanner rules have no fixture exercising them

## Rule Coverage Is Enforced

Every rule in `RISK_PATTERNS` and `FRAMEWORK_RULES` must have at least one fixture that
expects it. A rule with no positive fixture is reported in `uncoveredRules` and fails the
run. This keeps the headline numbers honest as rules are added.

## What These Numbers Mean

Fixtures are seeded: each unsafe fixture is a realistic loop with a known defect, and most
have a repaired twin that must produce zero findings. That design proves two things:

- the rule fires on the defect it was written for
- the rule stays quiet once the defect is fixed

It does not estimate how often these defects occur in real repositories, and it is not a
substitute for human review or agent evals. Treat it as a regression gate on the bundled
heuristics.
