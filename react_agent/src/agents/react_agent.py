"""Description: ReAct Agent class to manage the React Agent and its tools."""

from typing import Optional
from langchain_core.tools import StructuredTool
from langchain_core.messages import BaseMessage
from langchain.tools.base import BaseTool
from langchain.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent

from pydantic import BaseModel, Field


from react_agent.src.config.system_parameters import AgentSettings
from react_agent.src.util.llm_proxy import LLM_PROXY
from react_agent.src.util.logger import LoggerSingleton

AGENT_SETTINGS = AgentSettings()
LOGGER = LoggerSingleton.get_logger(AGENT_SETTINGS.logger_name)


class AgentResponseSchema(BaseModel):
    """Schema for the agent's response."""

    final_output: str = Field(..., description=AGENT_SETTINGS.final_output_description)
    reasoning: str = Field(..., description=AGENT_SETTINGS.reasoning_description)
    tools_used: list[str] = Field(
        ..., description=AGENT_SETTINGS.tools_used_description
    )


class ReActAgent:
    """ReAct Agent class to manage the React Agent and its tools."""

    def __init__(
        self,
        tool_list: list[BaseTool],
    ):
        self.last_agent_response: str = ""
        self.response_metadata: BaseMessage = None

        self.tools: list[BaseTool] = tool_list

        self.agent = create_react_agent(
            model=LLM_PROXY._llm,
            # response_format=AgentResponseSchema,
            tools=self.tools,
            prompt=self.create_sys_prompt(),
        )

    def create_sys_prompt(self) -> str:
        """Create the prompt for the agent based on AGENT_SYSTEM_PROMPT."""
        sys_prompt_template = PromptTemplate.from_template(AGENT_SETTINGS.system_prompt)

        return sys_prompt_template.format(
            react_instructions=("\n").join(AGENT_SETTINGS.instructions),
            tools=self.generate_tool_info_string(),
            rules=("\n").join(AGENT_SETTINGS.rules),
        )

    def generate_tool_info_string(self) -> str:
        """Generates a string containing tool names, arg schemas, and descriptions."""
        tool_strings = []
        for tool in self.tools:
            if isinstance(tool, StructuredTool):
                schema_props = tool.args_schema.get("properties")
            else:
                schema_props = tool.args_schema.model_json_schema().get("properties")

            arg_components = ", ".join(
                f"{name}: {prop['type']}" for name, prop in schema_props.items()
            )

            tool_strings.append(
                f"- Tool Name: {tool.name}, Description: {tool.description}, Args: {arg_components}"
            )

            LOGGER.debug("Tool Name: %s", tool.name)
        return "\n".join(tool_strings)

    def get_agent_graph(self) -> bytes:
        """Get the agent's graph in Mermaid format."""
        return self.agent.get_graph().draw_mermaid_png()

    def run_agent_with_input(
        self, user_message: str, debug: Optional[bool] = False
    ) -> str:
        """Evaluates user input if debug print the agent's stream of messages."""
        LOGGER.info(
            "Running agent synchronously with user message: %s",
            user_message.replace("\n", ""),
        )
        agent_final_message = None

        input_object = {"messages": [("user", user_message)]}

        config_object = {
            "recursion_limit": AGENT_SETTINGS.max_iterations,
        }

        if debug:
            for graph_response in self.agent.stream(
                input=input_object, stream_mode="values", config=config_object
            ):
                message = graph_response["messages"][-1]
                if isinstance(message, tuple):
                    print(message)
                else:
                    message.pretty_print()

                agent_final_message = message
        else:
            graph_response = self.agent.invoke(input=input_object, config=config_object)

            # Get the last message from the response (final answer)
            agent_final_message = graph_response["messages"][-1]

        LLM_PROXY.update_llm_usage(agent_final_message)
        self.response_metadata = graph_response
        self.last_agent_response = agent_final_message.content

        LOGGER.info("Agent final response: %s", self.last_agent_response)
        return self.last_agent_response

    async def arun_agent_with_input(
        self, user_message: str, debug: Optional[bool] = False
    ) -> str:
        """Evaluates user input if debug print stream of messages in an asynchronus manner."""
        LOGGER.info(
            "Running agent asynchronously with user message: %s",
            user_message.replace("\n", ""),
        )
        agent_final_message = None

        input_object = {"messages": [("user", user_message)]}

        config_object = {"recursion_limit": AGENT_SETTINGS.max_iterations}

        if debug:
            async for graph_response in self.agent.astream(
                input=input_object, stream_mode="values", config=config_object
            ):
                message = graph_response["messages"][-1]
                if isinstance(message, tuple):
                    print(message)
                else:
                    message.pretty_print()

                agent_final_message = message

        else:
            graph_response = await self.agent.ainvoke(
                input=input_object, config=config_object
            )
            # Get the last message from the response (final answer)
            agent_final_message = graph_response["messages"][-1]

        LLM_PROXY.update_llm_usage(agent_final_message)

        self.response_metadata = graph_response
        self.last_agent_response = agent_final_message.content

        LOGGER.info("Agent final response: %s", self.last_agent_response)
        return self.last_agent_response
