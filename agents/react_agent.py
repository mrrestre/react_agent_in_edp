import os
from dotenv import load_dotenv

from langgraph.prebuilt import create_react_agent

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool

from agents.prompts.prompts import AGENT_SYSTEM_PROMPT

from agents.config.agent_configs import PROFILE, PROMP_INSTRUCTIONS

from models.router import Router

from agent_tools.i_agent_tool import IAgentTool
from agent_tools.availability_checker import AvailabilityChecker
from agent_tools.email_writing import EmailWriter
from agent_tools.meeting_scheduling import MeetingScheduler


class ReActAgent:

    def __init__(self):
        self.last_input = None
        self.response = None

        self.tools = [
            self.define_tool(AvailabilityChecker),
            self.define_tool(EmailWriter),
            self.define_tool(MeetingScheduler),
        ]

        _ = load_dotenv()

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        self.llm_router = self.llm.with_structured_output(Router)

        self.agent = create_react_agent(
            model=self.llm, tools=self.tools, prompt=self.create_prompt
        )

    def define_tool(self, tool: IAgentTool):
        return Tool.from_function(
            func=tool.method,
            name=tool.name,
            description=tool.description,
            args_schema=tool.args_schema,
        )

    def create_prompt(self, state):
        return [
            {
                "role": "system",
                "content": AGENT_SYSTEM_PROMPT.format(
                    instructions=PROMP_INSTRUCTIONS["agent_instructions"], **PROFILE
                ),
            }
        ] + state["messages"]

    def run_agent(self, email):
        """result = self.llm_router.invoke(
            [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_prompt},
            ]
        )

        print(result)"""

        self.last_input = {"messages": [("user", str(email))]}

        self.response = self.agent.invoke(self.last_input)

    def print_agent_stream(self):
        for s in self.agent.stream(self.last_input, stream_mode="values"):
            message = s["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()
        print(f"Final response: {self.response}")

    def get_agent_graph(self):
        return self.agent.get_graph().draw_mermaid_png()
