# Contributing

LoopRight should stay small, portable, and practical.

## Guidelines

- Keep `skills/loopright/SKILL.md` concise.
- Put detailed domain guidance in `skills/loopright/references/`.
- Do not add runtime dependencies unless the skill cannot work without them.
- Prefer deterministic scripts for repeatable checks.
- Add examples when changing guidance for a loop category.

## Validation

Run:

```bash
python C:/Users/ashis/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/loopright
python skills/loopright/scripts/validate-loop-contract.py examples/retry-loop/loop-contract.md
```

