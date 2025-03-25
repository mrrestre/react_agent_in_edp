import os
from dotenv import load_dotenv

from langgraph.prebuilt import create_react_agent

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool

from agents.prompts.prompts import AGENT_SYSTEM_PROMPT

from config import agent_configs, LLM_configs

from models.router import Router

from agent_tools.i_agent_tool import IAgentTool
from agent_tools.availability_checker import AvailabilityChecker
from agent_tools.email_writing import EmailWriter
from agent_tools.meeting_scheduling import MeetingScheduler


class ReActAgent:

    def __init__(self, llm_to_use: LLM_configs.SupportedLLMs):
        self.input_object = None
        self.response = None

        self.tools = [
            self.define_tool(AvailabilityChecker),
            self.define_tool(EmailWriter),
            self.define_tool(MeetingScheduler),
        ]

        _ = load_dotenv()

        try:
            self.configure_llm(llm_to_use)
            self.agent = create_react_agent(
                model=self.llm, tools=self.tools, prompt=self.create_prompt
            )
        except ValueError as e:
            print(e)

    def configure_llm(self, llm: str) -> None:
        """Configure the LLM model to use, set up an environment variable to store the model name"""
        if llm == LLM_configs.SupportedLLMs.GEMINI_15_FLASH:
            used_model = LLM_configs.GEMINI_15_FLASH
            os.environ["LLM_IN_USE"] = used_model["name"]
            self.llm = ChatGoogleGenerativeAI(
                model=used_model["name"],
                google_api_key=os.getenv(used_model["key_name"]),
            )
        else:
            raise ValueError("Invalid LLM model")

    def define_tool(self, tool: IAgentTool) -> Tool:
        return Tool.from_function(
            func=tool.method,
            name=tool.name,
            description=tool.description,
            args_schema=tool.args_schema,
        )

    def create_prompt(self, state: dict) -> list:
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
        self.input_object = {"messages": [("user", str(email))]}

        self.response = self.agent.invoke(self.input_object)

    def get_agent_graph(self) -> str:
        return self.agent.get_graph().draw_mermaid_png()

    def print_agent_stream(self) -> None:
        for s in self.agent.stream(self.input_object, stream_mode="values"):
            message = s["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()

    def print_agent_response(self) -> None:
        self.response["messages"][-1].pretty_print()
