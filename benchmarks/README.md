# LoopRight Benchmarks

This benchmark suite measures deterministic scanner behavior over small unsafe and safe fixtures.

Run:

```bash
python benchmarks/run_loopright_benchmark.py
```

The benchmark reports:

- expected versus observed high-confidence risks
- missing findings
- unexpected findings
- precision and recall

It is intentionally small and dependency-free. Its job is to catch regressions in the bundled static risk heuristics, not to replace human review or agent evals.
