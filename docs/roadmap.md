# LoopRight Roadmap

Goal: make LoopRight the default skill agents reach for whenever repeated action can hang, drift, waste budget, overload systems, or claim success without proof.

## Value Flywheel

1. Collect real loop failures from code reviews, incidents, agent traces, and ML experiments.
2. Convert each failure into an example task.
3. Add the expected LoopRight contract, findings, correction, and evidence.
4. Add deterministic checks when a failure pattern is machine-detectable.
5. Keep `SKILL.md` concise and move details into focused references.
6. Validate examples in CI.
7. Maintain the machine-readable pattern catalog and generated agent resources.
8. Publish installable releases.

## Near-Term Enhancements

- Add a bundled `loopright.py` CLI front door for scan, doctor, validation, catalog, and template commands. Done.
- Add SARIF output for risk discovery so CI/code-scanning systems can consume LoopRight findings. Done.
- Add runnable pytest examples for retry and polling loops.
- Add a TypeScript/Node.js async concurrency example.
- Expand static pattern checks for high-risk constructs:
  - `while True` without budget terms nearby.
  - broad `except Exception` inside retry loops.
  - `asyncio.gather` over unbounded input.
  - polling loops without timeout or terminal failure states.
  - `Promise.all` over unbounded input.
  - benchmark or ML loops without fixed data versions.
- Add a `loopright-score` script that reports contract completeness, risk count, test coverage hints, and evidence quality.
- Add host-specific install docs for Codex, Claude Code, GitHub Copilot, Cursor, and Gemini CLI.

## Medium-Term Enhancements

- Package as a plugin or marketplace-ready skill bundle when the host ecosystem stabilizes.
- Add a benchmark suite where multiple agents solve the same loop tasks with and without LoopRight.
- Track pass rates over time.
- Add a publishable LoopRight pattern library surface from `catalog/loopright-patterns.json`.
- Add adapters that convert risk-discovery findings into Loop Doctor reports.
- Add examples from real domains:
  - ETL and backfills
  - web scraping and crawling
  - workflow orchestration
  - distributed jobs
  - stream processing
  - cost-bounded agent research

## Quality Bar

Do not accept vague examples. Every task should include:

- A concrete prompt.
- A risky starting point or scenario.
- A complete loop contract.
- Severity-ranked findings or implementation guidance.
- Tests or measurable completion evidence.
