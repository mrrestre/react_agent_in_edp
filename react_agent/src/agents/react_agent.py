"""Description: ReAct Agent class to manage the React Agent and its tools."""

from langgraph.prebuilt import create_react_agent

from langchain.tools.base import BaseTool
from langchain.prompts import PromptTemplate

from react_agent.src.util.llm_proxy import LLMProxy

from react_agent.src.config.system_parameters import AgentSettings

AGENT_SETTINGS = AgentSettings()


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
        sys_prompt_template = PromptTemplate.from_template(AGENT_SETTINGS.system_prompt)

        return sys_prompt_template.format(
            react_instructions=("\n").join(AGENT_SETTINGS.instructions),
            # tools=self.generate_tool_info_string(),
            tools="documentation_retriever, source_code_lookup, troubleshooting_memories_retriever",
            rules=("\n").join(AGENT_SETTINGS.rules),
        )

    # def generate_tool_info_string(self) -> str:
    #     """Generates a string containing tool names, arg schemas, and descriptions."""
    #     tool_strings = []
    #     for tool in self.tools:
    #         schema_props = tool.args_schema.model_json_schema().get("properties", {})
    #         arg_components = ", ".join(
    #             f"{name}: {prop['type']}" for name, prop in schema_props.items()
    #         )

    #         tool_strings.append(
    #             f"- Tool Name: {tool.name}, Description: {tool.description}, Args: {arg_components}"
    #         )
    #     return "\n".join(tool_strings)

    def get_agent_graph(self) -> str:
        """Get the agent's graph in Mermaid format."""
        return self.agent.get_graph().draw_mermaid_png()

    def run_and_print_agent_stream(self, user_message: str) -> None:
        """Evaluates user input and print the agent's stream of messages."""
        input_object = {"messages": [("user", user_message)]}

        config_object = {"recursion_limit": AGENT_SETTINGS.max_iterations}

        for s in self.agent.stream(
            input=input_object, stream_mode="values", config=config_object
        ):
            message = s["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()

    async def arun_and_print_agent_stream(self, user_message: str) -> None:
        """Evaluates user input and print stream of messages in an asynchronus manner."""
        input_object = {"messages": [("user", user_message)]}

        config_object = {"recursion_limit": AGENT_SETTINGS.max_iterations}

        async for output in self.agent.astream(
            input=input_object, stream_mode="values", config=config_object
        ):
            message = output["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()
