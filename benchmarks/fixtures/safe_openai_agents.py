"""OpenAI Agents SDK triage run with an explicit turn budget."""

from agents import Agent, Runner

triage = Agent(
    name="triage",
    instructions="Route the ticket and call tools as needed.",
    tools=[lookup_account, refund_order],
)


async def handle(ticket: str) -> str:
    outcome = await Runner.run(triage, ticket, max_turns=8)
    return outcome.final_output
