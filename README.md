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

## Where LoopRight Is Useful

LoopRight is most valuable when a loop is expensive, long-running, agent-driven, concurrent, or tied to external systems. These are the tasks where "just retry", "keep polling", or "iterate until it works" can quietly become runaway cost, duplicate side effects, bad metrics, or false completion.

Use it for high-skill engineering work such as:

- Reviewing architecture for bounded retries, polling, fan-out, and durable workflows.
- Designing distributed backfills, migrations, crawlers, and ETL jobs.
- Hardening async workers, queues, schedulers, and batch processors.
- Structuring ML training, evaluation, and hyperparameter-tuning loops.
- Controlling coding-agent repair loops so they stop repeating failed actions.
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
python skills/loopright/scripts/validate-loop-contract.py examples/retry-loop/loop-contract.md
```

## More Example Tasks

See [examples/tasks/README.md](examples/tasks/README.md) for additional tested prompts and LoopRight-style outputs across retry, polling, async batch, ML tuning, and agent repair loops.

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
