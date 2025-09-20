from dotenv import load_dotenv

load_dotenv()

from crewai import Crew, Agent, Task
from crewai.project import CrewBase, agent, task, crew
from tools import counter_tool


@CrewBase
class TranslatorCrew:

    @agent # role, goal, backstory
    def translator_agent(self):
        return Agent(
            config=self.agents_config['translator_agent']
        )
    
    @agent
    def counter_agent(self):
        return Agent(
            config=self.agents_config['counter_agent'],
            tools=[counter_tool]
        )

    @task # description, expected_output, agent
    def translate_task(self):
        return Task(
            config=self.tasks_config['translate_task']
            )
    
    @task
    def retranslate_task(self):
        return Task(
            config=self.tasks_config['retranslate_task']
            )
    
    @task
    def counter_task(self):
        return Task(
            config=self.tasks_config['counter_task']
        )
    
    @crew
    def assemble_crew(self):
        return Crew(
        agents=self.agents,
        tasks=self.tasks,
        verbose=True
        )


TranslatorCrew().assemble_crew().kickoff(
    inputs={
        'sentence': "i love seoul, korea"
        }
    )