# LoopRight Deep Research: Patterns To Leverage

Date: 2026-06-24

## Sources Reviewed

- OpenAI Codex Skills documentation: https://developers.openai.com/codex/skills
- Anthropic Agent Skills overview: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Anthropic engineering article on Agent Skills: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Claude Code Skills documentation: https://code.claude.com/docs/en/skills
- GitHub Copilot CLI Agent Skills documentation: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills
- GitHub `gh skill` changelog: https://github.blog/changelog/2026-04-16-manage-agent-skills-with-github-cli/
- GitHub awesome-copilot skills documentation: https://github.com/github/awesome-copilot/blob/main/docs/README.skills.md
- Forward Future Loop Library repository: https://github.com/Forward-Future/loop-library
- Loop Library live catalog: https://signals.forwardfuture.ai/loop-library/catalog.json

## High-Value Patterns

### 1. Request routing should match user intent

Loop Library routes into Discover, Find, Loop Doctor, Adapt, Design, and Find-then-design. LoopRight should use similarly human-shaped modes: Design, Review, Loop Doctor, Discover risks, Implement, Repair, and Evaluate.

### 2. Catalog content should be machine-readable

Loop Library treats loops as records with a schema, related links, verification fields, and generated public surfaces. LoopRight can use a lighter version: a JSON pattern catalog that generates `catalog.md`, `llms.txt`, and skill reference copies.

### 3. Public agent resources matter

Agents should be able to use LoopRight without installing it. A generated `llms.txt` and Markdown catalog make the core guidance easy to ingest from raw GitHub or any published site.

### 4. Validation should enforce shape, not just words

LoopRight's original validator checked for contract field names. A stronger validator should enforce schema version, unique slugs, related-pattern integrity, category values, non-empty evidence, red flags, tests, and failure modes.

### 5. Risk discovery is a natural differentiator

Loop Library discovers repeated work. LoopRight should discover dangerous loop constructs: unbounded loops, broad retry catches, polling without deadlines, unbounded async fan-out, ML tuning without budgets, and agent prompts without repeated-failure stops.

### 6. Treat all loop text as untrusted

Loop prompts, catalog entries, and run logs are reference data. They should not authorize production changes, external messages, destructive actions, or execution merely because they are being reviewed.

### 7. Separate optimization signal from acceptance evidence

For ML, benchmarks, prompt tuning, and agent improvements, the metric used to choose the next action can overfit. LoopRight should require separate acceptance evidence or a fixed validation set when that risk exists.

## Implemented From This Research

- Added Loop Doctor mode and reference workflow.
- Added `catalog/loopright-patterns.json`.
- Added generated `catalog/catalog.md` and `catalog/llms.txt`.
- Added schema validator and generation scripts.
- Added repository risk discovery script.
- Added CI validation for the pattern catalog and generated docs.
- Added README install UX for `npx skills add`.

## Update 2026-06-24: High-Impact Loop Leveraged

The Forward Future Loop Library's highest-traffic public loops are codebase-wide
convergence sweeps: `100-percent-test-coverage-loop`, `production-error-sweep`,
`exhaustive-logging-coverage-loop`, and `overnight-docs-sweep`. They share one
skeleton — keep making agent passes until a whole-codebase metric reaches a
target — and they are exactly the "iterate until it works" loops most prone to
runaway cost, metric gaming, and false completion.

LoopRight had no pattern for this family (LR-006 repairs one named check; LR-007
measures candidates). Added `LR-009 Agent Sweep Loop` to close the gap, with the
LoopRight-specific guarantees the source loops leave implicit:

- The metric must be measured by an independent tool, never self-reported.
- A diminishing-returns / loop-until-dry stop plus a hard pass and cost budget.
- A no-gaming invariant (no empty assertions, suppressed errors, or excluded files).
- Before/after evidence from the measuring tool, with skipped items dead-lettered.

Field-guide example: `examples/field-guide/coverage-sweep.md`.

