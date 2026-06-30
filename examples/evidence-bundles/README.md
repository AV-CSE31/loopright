# Loop Evidence Bundle Examples

These JSON files show how LoopRight can prove a completed loop run, not just design one.

Validate them with:

```bash
python ../../skills/loopright/scripts/loopright.py validate-run agent-repair-run.json
python ../../skills/loopright/scripts/loopright.py validate-run autonomous-quant-paper-run.json
```

Use evidence bundles when a reviewer, CI job, or another agent needs to know:

- the loop had a measurable contract,
- the run stayed inside budget,
- each iteration recorded hypothesis, action, progress, and checks,
- completion had artifacts or passing checks,
- side effects had permission boundaries and audit records,
- a verifier approved the result.
