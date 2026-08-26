"""CrewAI research crew with no per-agent iteration budget."""

from crewai import Agent, Crew, Task

researcher = Agent(
    role="Researcher",
    goal="Collect sources for the brief.",
    backstory="Digs through public filings.",
    tools=[search_tool],
)

brief = Task(description="Summarize the filings.", agent=researcher)
crew = Crew(agents=[researcher], tasks=[brief])
report = crew.kickoff()
