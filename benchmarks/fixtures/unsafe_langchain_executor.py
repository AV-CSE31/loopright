"""LangChain executor that keeps calling tools until the model stops."""

from langchain.agents import AgentExecutor, create_tool_calling_agent

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
answer = executor.invoke({"input": "Reconcile the ledger."})
