"""Description: ReAct Agent class to manage the React Agent and its tools."""

from langgraph.prebuilt import create_react_agent

from langchain.tools import Tool

from agents.prompts.prompts import AGENT_SYSTEM_PROMPT

from config import agent_configs, supported_llms

from util.llm_proxy import LLMProxy

from agent_tools.i_agent_tool import IAgentTool
from agent_tools.availability_checker import AvailabilityChecker
from agent_tools.email_writing import EmailWriter
from agent_tools.meeting_scheduling import MeetingScheduler


class ReActAgent:
    """ReAct Agent class to manage the React Agent and its tools."""

    def __init__(self, llm_to_use: supported_llms.SupportedLLMs):
        self.input_object = None
        self.response = None

        self.tools = [
            self.define_tool(AvailabilityChecker),
            self.define_tool(EmailWriter),
            self.define_tool(MeetingScheduler),
        ]

        llm_proxy = LLMProxy(model=llm_to_use, max_tokens=10000)

        self.agent = create_react_agent(
            model=llm_proxy.get_llm(), tools=self.tools, prompt=self.create_prompt
        )

    def define_tool(self, tool: IAgentTool) -> Tool:
        """Define a tool from an IAgentTool instance.
        Uses the method, name, description, and args_schema attributes."""
        return Tool.from_function(
            func=tool.method,
            name=tool.name,
            description=tool.description,
            args_schema=tool.args_schema,
        )

    def create_prompt(self, state: dict) -> list:
        """Create the prompt for the agent based on AGENT_SYSTEM_PROMPT and the state."""
        return [
            {
                "role": "system",
                "content": AGENT_SYSTEM_PROMPT.format(
                    instructions=agent_configs.PROMP_INSTRUCTIONS["agent_instructions"],
                    **agent_configs.PROFILE,
                ),
            }
        ] + state["messages"]

    def run_agent(self, email: str) -> None:
        """Run the agent with the ..."""
        self.input_object = {"messages": [("user", str(email))]}

        self.response = self.agent.invoke(self.input_object)

    def get_agent_graph(self) -> str:
        """Get the agent's graph in Mermaid format."""
        return self.agent.get_graph().draw_mermaid_png()

    def print_agent_stream(self) -> None:
        """Print the agent's stream of messages."""
        for s in self.agent.stream(self.input_object, stream_mode="values"):
            message = s["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()

    def print_agent_response(self) -> None:
        """Print the agent's final response"""
        self.response["messages"][-1].pretty_print()
