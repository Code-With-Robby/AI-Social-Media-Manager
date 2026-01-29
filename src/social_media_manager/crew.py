from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool
from typing import List

@CrewBase
class SocialMediaManager():
    """Dynamic Outreach Crew – Personalized interview invitations for any niche"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],  # type: ignore[index]
            verbose=True,
            tools=[SerperDevTool()]  # web search tool for real-time info
        )

    @agent
    def social_media_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['social_media_manager'],  # type: ignore[index]
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],  # type: ignore[index]
        )

    @task
    def dm_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['dm_generation_task'],  # type: ignore[index]
            output_file='generated_dm.txt'  # output file for the final DM
        )

    @crew
    def crew(self) -> Crew:
        """Creates the dynamic outreach crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=2,  # detailed logging (CrewAI supports int levels)
            # memory=True,  # optional - enable if you want conversation memory
            # planning=True,  # optional - enable for planning mode
        )
