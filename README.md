# LoopRight

Write loops right.

LoopRight is a portable Agent Skill for Codex, Claude Code, and other Agent Skills-compatible coding agents. It helps agents design, implement, review, and validate loops that are bounded, observable, failure-aware, and backed by completion evidence.

## What It Covers

- Finite `for` and `while` loops
- Retry and polling loops
- Async and concurrent loops
- Batch-processing loops
- ML training and hyperparameter-tuning loops
- Iterative code-repair loops
- Agent tool-use loops
- Durable workflow design review

LoopRight is not a runtime, API wrapper, task queue, retry framework, workflow engine, MCP server, or chatbot. The v0.1 product is procedural engineering knowledge plus deterministic supporting checks.

## Install

Copy or install the skill folder:

```text
skills/loopright/
```

The skill is self-contained and does not require files outside that directory.

## Use

```text
$loopright Review and improve this model fine-tuning loop.
```

```text
/loopright Add safe termination, measurable progress, pruning, and completion evidence to this Optuna workflow.
```

## Repository Layout

```text
skills/loopright/
  SKILL.md
  agents/openai.yaml
  references/
  scripts/
examples/
docs/
```

## Validation

Validate the skill metadata:

```bash
python C:/Users/ashis/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/loopright
```

Run the bundled loop contract check:

```bash
python skills/loopright/scripts/validate-loop-contract.py examples/retry-loop/loop-contract.md
```

