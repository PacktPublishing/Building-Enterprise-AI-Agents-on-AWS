import os
import requests
from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import tool
from crewai_tools import SerperDevTool

CLIENT_ID = os.environ["COGNITO_CLIENT_ID"]
CLIENT_SECRET = os.environ["COGNITO_CLIENT_SECRET"]
TOKEN_URL = os.environ["COGNITO_TOKEN_URL"]
SCOPE = os.environ["COGNITO_SCOPE"]
GATEWAY_URL = os.environ["AGENTCORE_GATEWAY_URL"]
TRAVEL_TOOL_NAME = os.environ["TRAVEL_TOOL_NAME"]
MCP_VERSION = "2026-07-28"

llm = LLM(model="bedrock/us.amazon.nova-pro-v1:0")
serper_dev_tool = SerperDevTool(api_key=os.environ.get("SERPER_API_KEY"))


def fetch_access_token():
    response = requests.post(
        TOKEN_URL,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={"grant_type": "client_credentials", "scope": SCOPE},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def mcp_meta():
    return {
        "io.modelcontextprotocol/protocolVersion": MCP_VERSION,
        "io.modelcontextprotocol/clientInfo": {"name": "vacation-planner", "version": "1.0.0"},
        "io.modelcontextprotocol/clientCapabilities": {},
    }


def call_tool(access_token, tool_name, arguments):
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "MCP-Protocol-Version": MCP_VERSION,
        "Mcp-Method": "tools/call",
        "Mcp-Name": tool_name,
    }
    payload = {
        "jsonrpc": "2.0",
        "id": "call-tool-request",
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments, "_meta": mcp_meta()},
    }
    response = requests.post(GATEWAY_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


@tool("Get Travel Packages")
def get_travel_packages(city: str) -> str:
    """Fetch the enterprise travel package for a supported city."""
    access_token = fetch_access_token()
    result = call_tool(access_token, TRAVEL_TOOL_NAME, {"city": city})
    return str(result)


@CrewBase
class VacationPlanner:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def vacation_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["vacation_researcher"],
            verbose=True,
            tools=[serper_dev_tool, get_travel_packages],
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
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential, verbose=True)
