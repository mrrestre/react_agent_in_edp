"""Description: ReAct Agent class to manage the React Agent and its tools."""

from langgraph.prebuilt import create_react_agent

from agents.prompts.prompts import AGENT_SYSTEM_PROMPT

from config import agent_configs

from util.llm_proxy import LLMProxy

from agent_tools.i_agent_tool import IAgentTool


class ReActAgent:
    """ReAct Agent class to manage the React Agent and its tools."""

    def __init__(self, llm_proxy: LLMProxy, tool_list: list[IAgentTool]):
        self.input_object = None
        self.response = None

        self.tools = tool_list

        self.agent = create_react_agent(
            model=llm_proxy.get_llm(), tools=self.tools, prompt=self.create_prompt
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
