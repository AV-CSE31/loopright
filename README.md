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

## Example Task Suite

See [examples/tasks/README.md](examples/tasks/README.md) for tested example prompts and LoopRight-style outputs across retry, polling, async batch, ML tuning, and agent repair loops.

## Research-Backed Skill Design

LoopRight follows patterns from OpenAI Codex, Claude Code, GitHub Copilot, and public Agent Skills repositories:

- A compact `SKILL.md` entry point.
- Progressive disclosure through targeted references.
- Deterministic scripts for repeatable validation.
- Representative example tasks as an eval harness.
- A self-contained installable skill folder.

See [docs/research/top-skill-patterns.md](docs/research/top-skill-patterns.md).

## Roadmap

See [docs/roadmap.md](docs/roadmap.md) for the value flywheel: eval tasks, deterministic checks, host portability, example coverage, and community contribution paths.
