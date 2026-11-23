from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.llm import LLM
from crewai_tools import SerperDevTool

import os
from datetime import datetime

search_tool = SerperDevTool()

llm_llama3 = LLM(
    model="ollama/llama3.1",
    base_url="http://localhost:11434"
)
llm_phi4 = LLM(
    model="ollama/phi4-mini",
    base_url="http://localhost:11434"
)

@CrewBase
class TallerCrewai():
    """TallerCrewai crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def investigador_tecnologias(self) -> Agent:
        return Agent(
            config=self.agents_config['investigador_minecraft'],
            verbose=True,
            llm=llm_llama3
        )

    @agent
    def redactor_informe(self) -> Agent:
        return Agent(
            config=self.agents_config['redactor_noticia'],
            verbose=True,
            llm=llm_phi4
        )

    @task
    def tarea_investigacion(self) -> Task:
        return Task(
            config=self.tasks_config['tarea_investigacion'],
        )

    @task
    def tarea_redaccion(self) -> Task:
        os.makedirs("informes", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return Task(
            config=self.tasks_config['tarea_redaccion'],
            output_file=f"informes/noticia_{timestamp}.md"
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )