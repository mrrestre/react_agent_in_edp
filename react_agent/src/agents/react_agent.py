"""Description: ReAct Agent class to manage the React Agent and its tools."""

from langgraph.prebuilt import create_react_agent

from langchain.tools.base import BaseTool
from langchain.prompts import PromptTemplate

from react_agent.src.config import promps_snippets

from react_agent.src.util.llm_proxy import LLMProxy

from react_agent.src.config.system_parameters import MAIN_AGENT


class ReActAgent:
    """ReAct Agent class to manage the React Agent and its tools."""

    def __init__(
        self,
        tool_list: list[BaseTool],
    ):
        self.response = None

        self.tools = tool_list

        self.agent = create_react_agent(
            model=LLMProxy().get_llm(),
            tools=self.tools,
            prompt=self.create_sys_prompt(),
        )

    def create_sys_prompt(self) -> str:
        """Create the prompt for the agent based on AGENT_SYSTEM_PROMPT."""
        sys_prompt_template = PromptTemplate.from_template(
            MAIN_AGENT.get("AGENT_SYSTEM_PROMPT")
        )

        return sys_prompt_template.format(
            react_instructions=promps_snippets.REACT_INSTRUCTIONS["instructions"],
            tools=self.generate_tool_info_string(),
        )

    def generate_tool_info_string(self) -> str:
        """Generates a string containing tool names, arg schemas, and descriptions."""
        tool_strings = []
        for tool in self.tools:
            schema_props = tool.args_schema.model_json_schema().get("properties", {})
            arg_components = ", ".join(
                f"{name}: {prop['type']}" for name, prop in schema_props.items()
            )

            tool_strings.append(
                f"- Tool Name: {tool.name}, Description: {tool.description}, Args: {arg_components}"
            )
        return "\n".join(tool_strings)

    def get_agent_graph(self) -> str:
        """Get the agent's graph in Mermaid format."""
        return self.agent.get_graph().draw_mermaid_png()

    def run_and_print_agent_stream(self, user_message: str) -> None:
        """Evaluates user input and print the agent's stream of messages."""
        input_object = {"messages": [("user", user_message)]}

        config_object = {"recursion_limit": MAIN_AGENT.get("MAX_ITERATIONS")}

        for s in self.agent.stream(
            input=input_object, stream_mode="values", config=config_object
        ):
            message = s["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()
