# Agent Framework Rulepacks

General static analysis finds source-level loop bugs but does not model agent execution
semantics: framework API edges, tool dispatch, handoffs, and agent re-entry. A tool loop
can be perfectly valid Python and still never terminate, because the only thing bounding
it is the model deciding to stop.

LoopRight's framework rulepacks close that gap with **guard-absence detection**. When a
file clearly builds an agent loop with a known framework and never mentions that
framework's own iteration guard, the loop is running on a library default rather than a
budget the design chose.

## Rules

| Rule | Framework | Fires when | Required guard |
|---|---|---|---|
| `langgraph-missing-recursion-limit` | LangGraph | `StateGraph(`, `MessageGraph(`, `create_react_agent(`, or `.compile(` | `recursion_limit` |
| `langgraph-missing-checkpointer` | LangGraph | `.compile(` in a LangGraph file | `checkpointer` or a `*Saver` |
| `openai-agents-missing-max-turns` | OpenAI Agents SDK | `Runner.run(`, `Runner.run_sync(`, `Runner.run_streamed(` | `max_turns` |
| `crewai-missing-iteration-budget` | CrewAI | `Agent(` or `Crew(` in a CrewAI file | `max_iter`, `max_execution_time`, or `max_rpm` |
| `langchain-agent-missing-max-iterations` | LangChain | `AgentExecutor(` or `initialize_agent(` | `max_iterations` or `max_execution_time` |
| `autogen-missing-turn-limit` | AutoGen | `initiate_chat(`, `GroupChat(`, `RoundRobinGroupChat(` | `max_turns`, `max_round`, `max_consecutive_auto_reply`, `max_messages`, or `termination_condition` |
| `ai-sdk-missing-step-limit` | Vercel AI SDK | `generateText(` or `streamText(` in a file importing `ai` and declaring `tools:` | `maxSteps` or `stopWhen` |

## How To Read A Finding

These rules are **file-scoped**. A guard configured in another module reads as missing
here. That is deliberate: the reviewer should be able to see the budget next to the loop
it bounds. Treat a finding as a review prompt with two valid answers:

1. The guard really is missing. Add it, then test that the loop stops on it.
2. The guard lives elsewhere. Say where, and consider moving or restating it at the call
   site so the next reader does not have to hunt for it.

## Why The Default Is Not A Budget

A framework default is a crash barrier, not a design decision:

- LangGraph raises `GraphRecursionError` at its default limit. That is an exception, not a
  terminal state with a recorded stop reason.
- Agents SDK, CrewAI, LangChain, and AutoGen defaults are chosen for demos, not for the
  cost profile or latency budget of a specific production loop.
- A tool-calling loop with no step ceiling is bounded only by the model's willingness to
  emit a final answer, which is not a property anyone can test.

The repair is always the same shape: choose the budget, make it visible at the call site,
and prove with a test that the loop stops on it and reports why.
