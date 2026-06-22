# Architecture

LoopRight is a standalone Agent Skill, not a runtime.

The installable unit is:

```text
skills/loopright/
```

Everything inside that folder must be sufficient for another agent to use the skill. Repository-level docs, examples, and CI are supporting materials only.

## Components

- `SKILL.md`: concise workflow and routing.
- `references/`: detailed guidance loaded only when needed.
- `scripts/`: deterministic helpers that can run without extra context.
- `agents/openai.yaml`: UI metadata.

