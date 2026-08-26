# Changelog

## Unreleased

- Added dependency-free runnable examples for retry, polling, and async worker loops.
- Added deterministic scanner benchmark fixtures and runner.
- Added pre-commit hook metadata and GitHub SARIF code-scanning workflow.
- Added case studies for retry cost, async fan-out, and agent repair churn.
- Added realistic field-guide examples for billing replay, embedding backfills, CI polling, realtime enrichment, and agent repair loops.
- Added an autonomous decision-loop pattern and paper-trading quant research field-guide example with maker-checker verification, state governance, connector boundaries, and kill-switch evidence.
- Added the agent-sweep loop pattern and a test-coverage-sweep field-guide example.
- Added agent framework rulepacks that flag LangGraph, OpenAI Agents SDK, CrewAI, LangChain, AutoGen, and Vercel AI SDK loops with no iteration guard in the file.
- Added guard-absence detection to the scanner, framework repair and evidence guidance to Loop Doctor, and a rulepack reference to the skill.
- Added published benchmark results with per-rule precision and recall, enforced rule coverage, and a CI drift check.
- Added a reusable GitHub Action at action.yml so other repositories can run LoopRight with one step.

## 0.1.0

- Initial LoopRight skill.
- Added loop contract workflow, reference guides, examples, and validator script.
