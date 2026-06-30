# Loop Evidence Bundles Research

Research date: 2026-06-30

## Research Question

What should LoopRight add next to become more useful in real engineering workflows, beyond design-time loop contracts and static risk discovery?

## Sources Reviewed

| Source | Pattern to leverage |
|---|---|
| [OpenTelemetry traces](https://opentelemetry.io/docs/concepts/signals/traces/) | Trace/span records make repeated work inspectable after execution. |
| [OpenAI Agents SDK tracing](https://openai.github.io/openai-agents-python/tracing/) | Agent runs benefit from structured traces that explain tool calls, handoffs, and intermediate steps. |
| [Promptfoo assertions](https://www.promptfoo.dev/docs/configuration/expected-outputs/) and [CI integration](https://www.promptfoo.dev/docs/integrations/github-action/) | Useful AI tooling turns expected behavior into machine-checkable assertions and CI gates. |
| [GitHub SARIF upload](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github) | Security and quality tools become more adoptable when findings can flow into standard review surfaces. |
| [LangSmith observability](https://docs.smith.langchain.com/observability) | Agent and LLM systems need traces, datasets, and evaluation artifacts to debug behavior over time. |
| [LangGraph durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution) | Long-running agent workflows need persisted state and replayable execution boundaries. |
| [Anthropic Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) and [OpenAI Codex skills](https://developers.openai.com/codex/skills) | Skills are strongest when the installable folder is compact, portable, and backed by deterministic helper scripts. |

## Findings

The strongest tooling pattern is not another prose checklist. It is a small machine-readable artifact that can move between an agent, CI, a reviewer, and an audit trail.

Top agent and evaluation tools are converging on four primitives:

1. **Structured traces:** record what happened, not only the final answer.
2. **Assertions and evaluators:** turn expected behavior into a pass/fail gate.
3. **CI-ready output:** let teams block bad runs before merge.
4. **Durable artifacts:** preserve command logs, metric tables, approvals, and side-effect records.

LoopRight already has design-time contracts and static discovery. The missing layer is post-run proof: a standard way to say "this loop ran, stopped for the right reason, stayed inside budget, and produced evidence a reviewer can verify."

## Current Limitation

LoopRight can require evidence, but before this change it did not define a machine-readable run evidence format. That left teams with a gap:

- agents could claim success without a structured audit record,
- reviewers could not quickly compare budget against actual usage,
- CI could not validate side-effect controls or verifier verdicts,
- run logs were hard to hand off between agents.

## Recommended Feature

Add **Loop Evidence Bundles**:

- a JSON template under the installable skill folder,
- a pure-Python validator under `skills/loopright/scripts`,
- realistic examples under `examples/evidence-bundles`,
- CI validation for sample bundles,
- README and skill entry-point guidance.

The bundle should validate:

- contract completeness,
- hard budget presence and actual usage,
- per-iteration hypothesis, action, progress, status, and checks,
- passing verifier for completed runs,
- artifacts or passed checks for completion,
- permission boundaries and idempotency/compensation for side effects,
- kill-switch confirmation,
- trace metadata and evaluation warnings.

## Why This Is High Leverage

Evidence bundles turn LoopRight from a design/review skill into a lifecycle tool:

- **Before execution:** define the loop contract.
- **During execution:** record iterations, checks, traces, and side effects.
- **After execution:** validate the run bundle before claiming completion.
- **In CI:** fail incomplete evidence bundles.
- **In reviews:** inspect a compact JSON summary instead of reading long agent transcripts.

This keeps the core skill lightweight and portable while aligning LoopRight with emerging observability, eval, and audit patterns.
