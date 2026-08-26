# LoopRight

Write loops right: bounded, observable, failure-aware, and backed by evidence.

[![Validate](https://github.com/AV-CSE31/loopright/actions/workflows/validate.yml/badge.svg)](https://github.com/AV-CSE31/loopright/actions/workflows/validate.yml)
[![Code Scanning](https://github.com/AV-CSE31/loopright/actions/workflows/loopright-code-scanning.yml/badge.svg)](https://github.com/AV-CSE31/loopright/actions/workflows/loopright-code-scanning.yml)
[![Scanner benchmark](https://img.shields.io/badge/scanner%20benchmark-14%2F14%20rules%20exercised-2ea44f)](benchmarks/RESULTS.md)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-portable-blue)](skills/loopright/SKILL.md)

LoopRight is a portable Agent Skill for Codex, Claude Code, and other Agent Skills-compatible coding agents. It helps agents design, implement, review, and validate loops that are bounded, observable, failure-aware, and backed by completion evidence.

It is built for the places where "just retry", "keep polling", "fan out everything", or "iterate until it works" can become runaway cost, duplicate side effects, overloaded services, bad metrics, or false completion.

## Why It Matters

LoopRight turns vague repeated work into an explicit engineering contract:

- What must improve each iteration.
- What must never change.
- What budget limits attempts, time, cost, memory, or concurrency.
- What failure conditions stop the loop.
- What evidence proves completion.

That makes it useful for code review, architecture design, incident repair, ML tuning, batch jobs, async workers, agent repair loops, and CI checks.

## Feature Highlights

| Feature | What it does | Where to look |
|---|---|---|
| Portable Agent Skill | Works as a self-contained `skills/loopright` folder for Codex, Claude Code, and compatible agents. | [skills/loopright/SKILL.md](skills/loopright/SKILL.md) |
| Loop Doctor | Diagnoses loop prompts, code, architecture, or run logs with verdict, findings, minimal repair, and required evidence. | [loop-doctor.md](skills/loopright/references/loop-doctor.md) |
| Loop Contract | Forces objective, state, action, progress, invariant, budget, stop, failure, recovery, and evidence before implementation. | [contract template](skills/loopright/templates/loop-contract-template.md) |
| Pattern Catalog | Machine-readable and human-readable loop patterns for retry, polling, fan-out, backfill, ML tuning, agent repair, agent sweeps, autonomous decisions, benchmarks, and durable workflows. | [catalog JSON](catalog/loopright-patterns.json), [catalog guide](catalog/catalog.md) |
| CLI Front Door | One command surface for scan, doctor, validation, catalog, and template operations. | [loopright.py](skills/loopright/scripts/loopright.py) |
| Risk Scanner | Detects risky loops such as unbounded `while True`, broad retry catches, polling without deadline, unbounded async fan-out, weak agent loops, and ML tuning without budget. | `python skills/loopright/scripts/loopright.py scan .` |
| Agent Framework Rulepacks | Flags LangGraph, OpenAI Agents SDK, CrewAI, LangChain, AutoGen, and Vercel AI SDK loops that never set their own iteration guard. | [rulepack reference](skills/loopright/references/agent-framework-rulepacks.md) |
| GitHub Action | Drop-in `uses: AV-CSE31/loopright@main` step that scans a repository and emits SARIF. | [action.yml](action.yml) |
| Published Benchmark Results | Precision, recall, and per-rule results regenerated on every change and diffed in CI. | [benchmarks/RESULTS.md](benchmarks/RESULTS.md) |
| SARIF Output | Emits code-scanning output that can be uploaded to GitHub Advanced Security or other SARIF consumers. | [.github/workflows/loopright-code-scanning.yml](.github/workflows/loopright-code-scanning.yml) |
| Pre-commit Hook | Lets teams block high-confidence loop risks before code lands. | [.pre-commit-hooks.yaml](.pre-commit-hooks.yaml) |
| Runnable Proof Pack | Standard-library examples with tests for retry loops, polling loops, and bounded async worker pools. | [examples/runnable](examples/runnable) |
| Scanner Benchmark | Deterministic benchmark over safe and unsafe fixtures with precision, recall, false positive, and false negative reporting. | [benchmarks](benchmarks) |
| Field Guide Examples | Realistic examples with bad starting points, operational constraints, contracts, repair plans, and evidence. | [examples/field-guide](examples/field-guide) |
| Agent-ready Guide | `llms.txt` and generated catalog docs let agents use LoopRight context even before installing the skill. | [llms.txt](catalog/llms.txt) |

## What It Covers

- Finite `for` and `while` loops
- Retry and polling loops
- Async and concurrent loops
- Batch-processing loops
- ML training and hyperparameter-tuning loops
- Iterative code-repair loops
- Agent tool-use loops
- Agent framework loops in LangGraph, OpenAI Agents SDK, CrewAI, LangChain, AutoGen, and the Vercel AI SDK
- Autonomous decision loops with state, verifier, connector, audit, and kill-switch boundaries
- Durable workflow design review

LoopRight is not a runtime, API wrapper, task queue, retry framework, workflow engine, MCP server, or chatbot. The v0.1 product is procedural engineering knowledge plus deterministic supporting checks.

## Public Agent Resources

LoopRight can be used even before installation:

- [Machine-readable pattern catalog](catalog/loopright-patterns.json)
- [Human-readable pattern catalog](catalog/catalog.md)
- [Agent guide / llms.txt](catalog/llms.txt)

The catalog includes patterns for retry loops, polling loops, async fan-out, distributed backfills, ML tuning, agent repair, agent sweeps, autonomous decisions, benchmark loops, and durable workflows.

## Practical Tooling

LoopRight also ships a pure-Python command front door inside the installable skill folder. It uses only the standard library and sibling files under `skills/loopright`, so the skill still works when copied by itself.

Scan a repository for risky loops:

```bash
python skills/loopright/scripts/loopright.py scan . --format md
```

Generate machine-readable output:

```bash
python skills/loopright/scripts/loopright.py scan . --format json
python skills/loopright/scripts/loopright.py scan . --format sarif --output loopright.sarif
```

Scan agent-framework code for loops that never set their own iteration guard:

```bash
python skills/loopright/scripts/loopright.py scan services/agents --format md
```

This reports LangGraph graphs without `recursion_limit` or a checkpointer, Agents SDK runs without `max_turns`, CrewAI agents without `max_iter`, LangChain executors without `max_iterations`, AutoGen chats without a turn ceiling, and Vercel AI SDK tool loops without `maxSteps` or `stopWhen`. See the [rulepack reference](skills/loopright/references/agent-framework-rulepacks.md) for how to read a finding.

Turn a file, prompt, or run log into a Loop Doctor report:

```bash
python skills/loopright/scripts/loopright.py doctor path/to/file.py
```

Validate contracts and catalog data:

```bash
python skills/loopright/scripts/loopright.py validate-contract examples/retry-loop/loop-contract.md
python skills/loopright/scripts/loopright.py validate-contracts examples
python skills/loopright/scripts/loopright.py validate-catalog
```

Print bundled references from the installed skill:

```bash
python skills/loopright/scripts/loopright.py catalog --format md
python skills/loopright/scripts/loopright.py catalog --format llms
python skills/loopright/scripts/loopright.py template
```

## Proof Pack

Run dependency-free examples that show unsafe loop ideas repaired into bounded implementations:

```bash
python -m unittest discover -s examples/runnable/python -p "test_*.py"
```

Run the deterministic scanner benchmark:

```bash
python benchmarks/run_loopright_benchmark.py
```

The benchmark checks known unsafe and safe fixtures and reports precision, recall, false positives, and false negatives for high-confidence scanner findings.

Current published results ([full table](benchmarks/RESULTS.md)):

| Metric | Value |
|---|---|
| Precision (high-confidence findings) | 100.0% |
| Recall (high-confidence findings) | 100.0% |
| Fixtures | 16 |
| Rules exercised | 14/14 |
| Safe fixtures with zero findings | 5/5 |

These are seeded fixtures, not a random sample of production code. They prove every rule
fires where it should and stays quiet on the repaired version of the same loop, and they
fail CI when a rule regresses. They do not estimate real-world prevalence. Every scanner
rule must have a positive fixture or the benchmark fails, so coverage cannot silently rot.

Case studies:

- [Runaway retry cost](docs/case-studies.md#runaway-retry-cost)
- [Unbounded async fan-out](docs/case-studies.md#unbounded-async-fan-out)
- [Coding-agent repair churn](docs/case-studies.md#coding-agent-repair-churn)

Field guide examples with realistic prompts, risky starting points, LoopRight contracts, repairs, and required evidence:

- [Billing webhook replay](examples/field-guide/billing-webhook-replay.md)
- [Embedding backfill](examples/field-guide/embedding-backfill.md)
- [CI job poller](examples/field-guide/ci-job-poller.md)
- [Realtime enrichment fan-out](examples/field-guide/realtime-enrichment-fanout.md)
- [Support agent repair loop](examples/field-guide/support-agent-repair-loop.md)
- [Autonomous quant research loop](examples/field-guide/autonomous-quant-research-loop.md)
- [Test coverage sweep](examples/field-guide/coverage-sweep.md)

## Adoption Hooks

Use LoopRight with pre-commit:

```yaml
repos:
  - repo: https://github.com/AV-CSE31/loopright
    rev: main
    hooks:
      - id: loopright-scan
```

Use LoopRight as a GitHub Action. The action is defined at [action.yml](action.yml) and needs no installation step:

```yaml
name: Loop safety

on: [pull_request]

permissions:
  contents: read
  security-events: write

jobs:
  loopright:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: AV-CSE31/loopright@main
        with:
          path: .
          format: sarif
          output: loopright.sarif
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: loopright.sarif
```

Inputs: `path` (default `.`), `format` (`sarif`, `json`, or `md`), `output`, `fail-on-risk` (default `false`), and `python-version`. Set `fail-on-risk: "true"` to block a pull request on high-confidence findings instead of only reporting them.

This repository dogfoods the same action in [.github/workflows/loopright-code-scanning.yml](.github/workflows/loopright-code-scanning.yml).

## Where LoopRight Is Useful

LoopRight is most valuable when a loop is expensive, long-running, agent-driven, concurrent, or tied to external systems. These are the tasks where "just retry", "keep polling", or "iterate until it works" can quietly become runaway cost, duplicate side effects, bad metrics, or false completion.

Use it for high-skill engineering work such as:

- Reviewing architecture for bounded retries, polling, fan-out, and durable workflows.
- Designing distributed backfills, migrations, crawlers, and ETL jobs.
- Hardening async workers, queues, schedulers, and batch processors.
- Structuring ML training, evaluation, and hyperparameter-tuning loops.
- Controlling coding-agent repair loops so they stop repeating failed actions.
- Auditing autonomous agent loops that use state files, verifiers, connectors, and kill switches.
- Designing research or benchmark loops with budgets, progress signals, and evidence.
- Auditing workflow engines or orchestration code before it ships.

## Practical Examples

### 1. Architecture Review For A Distributed Backfill

Prompt:

```text
$loopright Review the architecture for a customer-record backfill that will scan 180M rows,
call a third-party enrichment API, write normalized records, and resume after deploys.
```

LoopRight should force the design to answer:

| Element | Example answer |
|---|---|
| Objective | Backfill all eligible customer rows exactly once and produce a reconciliation report. |
| State | Cursor position, processed ids, API result cache, failed ids, checkpoint version. |
| Action | Read a bounded page, enrich records, write normalized output, checkpoint progress. |
| Progress | Processed row count increases and checkpoint advances monotonically. |
| Invariant | No customer id is written twice for the same backfill version. |
| Budget | Max page size, API rate limit, daily cost cap, job deadline, retry budget per row. |
| Stop condition | All eligible ids are terminal: written, skipped, or dead-lettered. |
| Failure condition | Error rate threshold exceeded, checkpoint corruption, API quota exhaustion. |
| Recovery | Resume from checkpoint, skip already-written ids, dead-letter repeated failures. |
| Evidence | Row counts reconcile, checksum report saved, dead-letter report reviewed. |

What it catches:

- Unbounded scans without checkpoints.
- Duplicate writes after retry or deploy.
- No API rate-limit policy.
- No reconciliation evidence.
- No clear dead-letter or resume behavior.

### 2. Async Worker Pool For A High-Volume Pipeline

Prompt:

```text
$loopright Refactor this asyncio pipeline that creates one task per event from Kafka.
It must process 50k events/minute without overwhelming downstream services.
```

LoopRight should guide the agent toward:

- Bounded concurrency with a task group, queue, semaphore, or worker pool.
- Explicit partial-failure policy: retry, dead-letter, or fail the batch.
- Cancellation propagation and idempotent cleanup.
- Metrics for active workers, queue depth, success count, failure count, and latency.
- Tests for zero input, max concurrency, partial failure, timeout, and cancellation.

Example completion evidence:

```text
Processed 1,000 synthetic events with max_active_workers=32.
0 duplicate writes.
17 expected downstream failures were dead-lettered.
Cancellation test passed with no leaked tasks.
```

### 3. ML Tuning Loop With Real Evidence

Prompt:

```text
$loopright Design an Optuna tuning loop for a fraud model.
We need better recall without increasing false positives beyond 3%.
```

LoopRight should prevent vague "optimize model" behavior by requiring:

- Baseline precision, recall, false-positive rate, and validation split id.
- Objective metric and direction.
- Trial budget or wall-clock deadline.
- Search space and pruning rule.
- Failed-trial handling.
- Final comparison against baseline.
- Saved report with best parameters, metric table, seed, and data version.

High-quality final evidence:

```text
Baseline recall: 0.713 at FPR 0.029
Best trial recall: 0.748 at FPR 0.030
Trials used: 46/50
Pruned trials: 11
Report: tuning-report.json
Validation split: fraud-val-2026-06
```

### 4. Coding-Agent Repair Loop

Prompt:

```text
$loopright Create a repair loop for an agent fixing a flaky checkout test.
The agent may inspect code, edit files, and run tests, but must not churn forever.
```

LoopRight should define the agent's operating contract:

- Reproduce the failure once.
- Keep a current hypothesis.
- Make one focused edit per cycle.
- Run the narrow deterministic check.
- Stop if the same failure repeats three times without a changed hypothesis.
- Preserve unrelated user changes.
- Escalate when the requirement or fixture behavior is ambiguous.

Evidence before completion:

```text
Command: pytest tests/checkout/test_payment_retry.py -q
Result: 6 passed
Cycles used: 3/6
Changed files: checkout/retry_policy.py, tests/checkout/test_payment_retry.py
Repeated-failure guard: not triggered
```

### 5. Durable Workflow Orchestration Review

Prompt:

```text
$loopright Review this order-fulfillment workflow before we move it to production.
It has payment capture, inventory reservation, shipping label creation, and compensation.
```

LoopRight should focus the architecture review on:

- Which steps are idempotent and which require dedupe keys.
- Which retries are safe and which need compensation.
- Where the durable runtime owns persistence, scheduling, and replay.
- Timeout and cancellation behavior for human or vendor delays.
- Evidence for terminal states: fulfilled, cancelled, refunded, failed, or manual-review.

Findings it should surface:

- Retrying payment capture without an idempotency key is a P0/P1 risk.
- Polling shipping status without a deadline can strand workflows.
- Compensation actions need their own budgets and evidence.
- Workflow replay must not repeat non-idempotent side effects.

### 6. Research Or Benchmark Loop With Budget Control

Prompt:

```text
$loopright Design a benchmark loop that tests 12 agent prompts across 8 repositories,
collects pass rates, and stops when results are statistically useful or budget is exhausted.
```

LoopRight should require:

- A measurable objective: pass rate, cost, latency, regression count.
- Fixed dataset and repository versions.
- Max runs, max spend, and max wall-clock time.
- Random seed or sampling plan.
- Failure handling for flaky repos or infrastructure errors.
- Evidence artifact: CSV/JSON results, summary table, and reproduction command.

This prevents benchmark loops from becoming open-ended "try more prompts" sessions without a stopping rule.

## Install

LoopRight is portable because the installable unit is just the skill folder:

```text
skills/loopright/
```

The skill is self-contained and does not require files outside that directory.

### One-Command Install

If you use the Agent Skills installer, install LoopRight from GitHub:

```bash
npx skills add AV-CSE31/loopright --skill loopright --agent codex -g -y
```

Claude Code:

```bash
npx skills add AV-CSE31/loopright --skill loopright --agent claude-code -g -y
```

Install for both:

```bash
npx skills add AV-CSE31/loopright \
  --skill loopright \
  --agent codex \
  --agent claude-code \
  -g -y
```

Leave off `-g` to install only in the current project. Leave off `-y` to review prompts interactively.

### Install In Codex

Codex discovers Agent Skills from `.agents/skills` in a repository, from parent `.agents/skills` folders up to the repository root, and from the user-level `$HOME/.agents/skills` directory.

Project install:

```bash
mkdir -p .agents/skills
cp -R skills/loopright .agents/skills/loopright
```

User install:

```bash
mkdir -p ~/.agents/skills
cp -R skills/loopright ~/.agents/skills/loopright
```

Then start or restart Codex in the repository and invoke:

```text
$loopright Review this polling loop for termination, failure handling, and completion evidence.
```

If the skill does not appear, restart Codex. Codex can also invoke it implicitly when the task matches the skill description.

### Install In Claude Code

Claude Code discovers skills from `.claude/skills` in a project and from `~/.claude/skills` for personal skills.

Project install:

```bash
mkdir -p .claude/skills
cp -R skills/loopright .claude/skills/loopright
```

User install:

```bash
mkdir -p ~/.claude/skills
cp -R skills/loopright ~/.claude/skills/loopright
```

Then start Claude Code with:

```bash
claude
```

Invoke the skill directly:

```text
/loopright Review this retry loop for budgets, idempotency, and evidence.
```

Claude Code watches existing skill directories for changes, but if you create a new top-level skills directory while Claude Code is already running, restart Claude Code.

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
python skills/loopright/scripts/loopright.py validate-contract examples/retry-loop/loop-contract.md
```

Validate the pattern catalog:

```bash
python skills/loopright/scripts/loopright.py validate-catalog catalog/loopright-patterns.json
```

Regenerate public catalog files:

```bash
python skills/loopright/scripts/generate-pattern-docs.py catalog/loopright-patterns.json catalog
```

Discover loop risks in a repository:

```bash
python skills/loopright/scripts/loopright.py scan .
```

This repository includes intentional unsafe snippets in `examples/` and `benchmarks/fixtures/` to demonstrate LoopRight findings. For a clean self-scan of the tool code, run:

```bash
python skills/loopright/scripts/loopright.py scan skills/loopright/scripts --fail-on-risk
```

## More Example Tasks

See [examples/tasks/README.md](examples/tasks/README.md) for additional tested prompts and LoopRight-style outputs across retry, polling, async batch, ML tuning, and agent repair loops.

See [examples/runnable/README.md](examples/runnable/README.md) for dependency-free runnable examples with tests.

See [examples/field-guide/README.md](examples/field-guide/README.md) for more realistic examples that include operational constraints, bad starting points, repair plans, and evidence.

## Research-Backed Skill Design

LoopRight follows patterns from OpenAI Codex, Claude Code, GitHub Copilot, and public Agent Skills repositories:

- A compact `SKILL.md` entry point.
- Progressive disclosure through targeted references.
- Deterministic scripts for repeatable validation.
- Representative example tasks as an eval harness.
- A self-contained installable skill folder.

See [docs/research/top-skill-patterns.md](docs/research/top-skill-patterns.md).
See [docs/research/loop-library-leverage-deep-research.md](docs/research/loop-library-leverage-deep-research.md) for the Loop Library comparison and implementation notes.

## Roadmap

See [docs/roadmap.md](docs/roadmap.md) for the value flywheel: eval tasks, deterministic checks, host portability, example coverage, and community contribution paths.
