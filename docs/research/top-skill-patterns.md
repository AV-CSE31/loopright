# Top Agent Skill Patterns Research

Date: 2026-06-22

## Sources Reviewed

- OpenAI Codex Agent Skills documentation: https://developers.openai.com/codex/skills
- Anthropic Agent Skills overview: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Anthropic engineering article on Agent Skills: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Claude Code skills documentation: https://code.claude.com/docs/en/skills
- GitHub Copilot CLI Agent Skills documentation: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills
- GitHub Changelog for `gh skill`: https://github.blog/changelog/2026-04-16-manage-agent-skills-with-github-cli/
- GitHub awesome-copilot skills documentation: https://github.com/github/awesome-copilot/blob/main/docs/README.skills.md
- Anthropic public skills repository: https://github.com/anthropics/skills

## Patterns To Borrow

### 1. Optimize the trigger description

Codex and Copilot both choose skills from the skill description before loading the full `SKILL.md`. OpenAI specifically recommends concise descriptions with clear scope and boundaries because descriptions may be shortened in large skill sets.

LoopRight implication: keep the description front-loaded with trigger words such as retry, polling, async concurrency, ML tuning, iterative repair, and agent loops.

### 2. Keep `SKILL.md` lean

OpenAI and Anthropic both describe progressive disclosure: metadata first, then `SKILL.md`, then optional references/scripts/assets. Anthropic recommends splitting large or mutually exclusive contexts into separate files.

LoopRight implication: `SKILL.md` should stay as the operating workflow. Domain-specific depth belongs in `references/`.

### 3. Bundle deterministic scripts

Anthropic emphasizes that some operations are better handled by executable code for deterministic reliability and lower token cost.

LoopRight implication: validators should remain scripts. The next frontier is not more prose; it is checks that catch missing contracts and incomplete examples.

### 4. Build from evals, not vibes

Anthropic recommends starting with representative tasks, observing where agents struggle, then building skills incrementally around those gaps.

LoopRight implication: the example task suite is a first eval set. Every meaningful change should add or improve a task that demonstrates the behavior.

### 5. Design for portability

GitHub notes Agent Skills work across multiple hosts, and `gh skill` adds install/version workflows. GitHub Copilot supports project and personal skill locations, while Claude Code discovers filesystem-based skills.

LoopRight implication: the installable skill must stay self-contained under `skills/loopright`, while repository docs explain host-specific installation.

### 6. Make usage obvious

Public skill collections emphasize example usage, install instructions, and clear contribution paths.

LoopRight implication: include examples, expected outputs, test reports, templates, and contribution rules so users can quickly judge usefulness.

## Enhancement Plan

1. Add operating modes and required output shapes to `SKILL.md`.
2. Add a reusable loop contract template.
3. Add a recursive validator for example contracts.
4. Expand the review rubric with missing-evidence patterns and a test matrix.
5. Keep developing the example task suite as the skill's eval harness.

