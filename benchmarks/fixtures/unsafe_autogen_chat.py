"""AutoGen two-agent chat with no turn ceiling or termination condition."""

import autogen

assistant = autogen.AssistantAgent("assistant", llm_config={"model": "gpt-4o"})
user = autogen.UserProxyAgent("user", human_input_mode="NEVER")

user.initiate_chat(assistant, message="Refactor the billing module.")
