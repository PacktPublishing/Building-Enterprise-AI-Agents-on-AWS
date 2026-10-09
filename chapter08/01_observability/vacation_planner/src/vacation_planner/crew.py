import os
from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()
aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
model_id = os.environ["BEDROCK_MODEL_ID"]
llm = LLM(model=model_id, region_name=aws_region)
search_tool = SerperDevTool(api_key=os.environ.get("SERPER_API_KEY"))


@CrewBase
class VacationPlanner:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def vacation_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["vacation_researcher"],
            verbose=True,
            tools=[search_tool],
            llm=llm,
        )

    @agent
    def itinerary_planner(self) -> Agent:
        return Agent(
            config=self.agents_config["itinerary_planner"],
            verbose=True,
            llm=llm,
        )

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"])

    @task
    def reporting_task(self) -> Task:
        return Task(config=self.tasks_config["reporting_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


@app.entrypoint
def agent_invocation(payload, context):
    topic = str(payload.get("topic") or payload.get("prompt") or "").strip()
    if not topic:
        return {"error": "topic is required"}

    result = VacationPlanner().crew().kickoff(inputs={"topic": topic})
    return {"result": result.raw}


if __name__ == "__main__":
    app.run(port=8080)
