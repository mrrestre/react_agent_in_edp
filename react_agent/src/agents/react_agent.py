"""Description: ReAct Agent class to manage the React Agent and its tools."""

import json
import time
from typing import Optional
from langchain_core.tools import StructuredTool
from langchain_core.messages import BaseMessage, AIMessage
from langchain.tools.base import BaseTool
from langchain.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent

from pydantic import BaseModel


from react_agent.src.config.system_parameters import AgentSettings, LlmProxySettings
from react_agent.src.util.llm_proxy import LLM_PROXY
from react_agent.src.util.logger import LoggerSingleton

LLM_PROXY_SETTINGS = LlmProxySettings()
AGENT_SETTINGS = AgentSettings()
LOGGER = LoggerSingleton.get_logger(AGENT_SETTINGS.logger_name)


class ToolCall(BaseModel):
    """Schema for tool call properties"""

    tool_name: str
    arguments: Optional[dict[str, str]]


class AgentRun(BaseModel):
    """Schema for the agent run data."""

    final_output: str
    tools_used: list[ToolCall]
    excecution_time_seconds: float
    model_used: str

    def pretty_print(self):
        """Print excecution summary nicely"""
        print("Agent Run Summary")
        print("=" * 40)
        print(f"Final Output:\n{self.final_output.content}\n")
        print(f"Model Used:\n{self.model_used}\n")
        print(f"Execution Time: {self.excecution_time_seconds} seconds\n")

        print("Tools Used:")
        if not self.tools_used:
            print("  None")
        else:
            for i, tool in enumerate(self.tools_used, start=1):
                print(f"  Tool #{i}:")
                print(f"    Name: {tool.tool_name}")
                print("    Arguments:")
                for arg_key, arg_value in tool.arguments.items():
                    print(f"      {arg_key}: {arg_value}")
        print("=" * 40)


class ReActAgent:
    """ReAct Agent class to manage the React Agent and its tools."""

    def __init__(
        self,
        tool_list: list[BaseTool],
    ):
        self.run_data: AgentRun = AgentRun(
            final_output="",
            tools_used=[],
            excecution_time_seconds=0.0,
            model_used=LLM_PROXY_SETTINGS.model,
        )

        self.available_tools: list[BaseTool] = tool_list

        self.agent = create_react_agent(
            model=LLM_PROXY._llm,
            tools=self.available_tools,
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
        for tool in self.available_tools:
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
    ) -> None:
        """Evaluates user input if debug print the agent's stream of messages."""
        LOGGER.info(
            "Running agent synchronously with user message: %s",
            user_message.replace("\n", ""),
        )

        input_object = {"messages": [("user", user_message)]}

        config_object = {
            "recursion_limit": AGENT_SETTINGS.max_iterations,
        }

        run_start_time = time.perf_counter()
        if debug:
            for message_list in self.agent.stream(
                input=input_object, stream_mode="values", config=config_object
            ):
                message = message_list["messages"][-1]
                if isinstance(message, tuple):
                    print(message)
                else:
                    message.pretty_print()
        else:
            message_list = self.agent.invoke(input=input_object, config=config_object)
        run_end_time = time.perf_counter()

        self._post_process_agent_run(
            message_list["messages"], run_end_time - run_start_time
        )

        LOGGER.info("Agent final response: %s", self.run_data.final_output)

    async def arun_agent_with_input(
        self, user_message: str, debug: Optional[bool] = False
    ) -> None:
        """Evaluates user input if debug print stream of messages in an asynchronus manner."""
        LOGGER.info(
            "Running agent asynchronously with user message: %s",
            user_message.replace("\n", ""),
        )

        input_object = {"messages": [("user", user_message)]}

        config_object = {"recursion_limit": AGENT_SETTINGS.max_iterations}

        run_start_time = time.perf_counter()
        if debug:
            async for message_list in self.agent.astream(
                input=input_object, stream_mode="values", config=config_object
            ):
                message = message_list["messages"][-1]
                if isinstance(message, tuple):
                    print(message)
                else:
                    message.pretty_print()

        else:
            message_list = await self.agent.ainvoke(
                input=input_object, config=config_object
            )
        run_end_time = time.perf_counter()

        self._post_process_agent_run(
            message_list["messages"], run_end_time - run_start_time
        )

        LOGGER.info("Agent final response: %s", self.run_data.final_output)

    def _post_process_agent_run(
        self, execution_messages: list[BaseMessage], run_time: float
    ) -> None:
        """Gather run information and extract final response"""
        # Set the final agent message as the response from the run
        self.run_data.final_output = execution_messages[-1]
        self.run_data.excecution_time_seconds = round(run_time, 3)

        for message in execution_messages:
            if isinstance(message, AIMessage) and message.additional_kwargs.get(
                "tool_calls"
            ):
                for tool_call in message.additional_kwargs.get("tool_calls"):
                    if tool_call.get("function"):
                        self.run_data.tools_used.append(
                            ToolCall(
                                tool_name=tool_call["function"]["name"],
                                arguments=json.loads(
                                    tool_call["function"]["arguments"]
                                ),
                            )
                        )
                    else:
                        continue

        LLM_PROXY.update_llm_usage(self.run_data.final_output)

    def get_execution_metadata(self) -> AgentRun:
        """Help function for getting execution metadata"""
        return self.run_data
