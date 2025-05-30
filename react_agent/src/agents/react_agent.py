"""Description: ReAct Agent class to manage the React Agent and its tools."""

import json
import re
import time
from typing import Optional
from langchain_core.tools import StructuredTool
from langchain_core.messages import BaseMessage, AIMessage
from langchain.tools.base import BaseTool
from langchain.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent

from react_agent.src.agents.models.react_agent_models import AgentRun, ToolCall
from react_agent.src.config.system_parameters import AgentSettings, LlmProxySettings
from react_agent.src.util.llm_proxy import LLM_PROXY
from react_agent.src.util.logger import LoggerSingleton

LLM_PROXY_SETTINGS = LlmProxySettings()
AGENT_SETTINGS = AgentSettings()
LOGGER = LoggerSingleton.get_logger(AGENT_SETTINGS.logger_name)


class ReActAgent:
    """ReAct Agent class to manage the React Agent and its tools."""

    def __init__(
        self,
        tool_list: list[BaseTool],
    ):
        self.run_data: AgentRun = AgentRun(
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
        if AGENT_SETTINGS.use_tool_rankings:
            sys_prompt_template = PromptTemplate.from_template(
                AGENT_SETTINGS.system_prompt_tool_rankings
            )

            tool_rankings = ""
            for tool in self.available_tools:
                if AGENT_SETTINGS.tool_rankings.get(tool.name):
                    tool_rankings += f"Tool name: {tool.name}, Ranking: {AGENT_SETTINGS.tool_rankings.get(tool.name)}\n"
                elif AGENT_SETTINGS.mcp_tool_ranking.get(tool.name):
                    tool_rankings += f"Tool name: {tool.name}, Ranking: {AGENT_SETTINGS.mcp_tool_ranking.get(tool.name)}\n"

            return sys_prompt_template.format(
                react_instructions=("\n").join(
                    AGENT_SETTINGS.reasoning_model_instructions
                    if LLM_PROXY_SETTINGS.is_reasoning_model
                    else AGENT_SETTINGS.react_instructions
                ),
                tools=self.generate_tool_info_string(),
                rules=("\n").join(AGENT_SETTINGS.rules_tool_rankings),
                tool_rankings=tool_rankings,
            )
        else:
            sys_prompt_template = PromptTemplate.from_template(
                AGENT_SETTINGS.system_prompt
            )

            return sys_prompt_template.format(
                react_instructions=("\n").join(
                    AGENT_SETTINGS.reasoning_model_instructions
                    if LLM_PROXY_SETTINGS.is_reasoning_model
                    else AGENT_SETTINGS.react_instructions
                ),
                tools=self.generate_tool_info_string(),
                rules=("\n").join(AGENT_SETTINGS.rules_tool_memory),
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
            "recursion_limit": (
                AGENT_SETTINGS.max_iterations_reasoning_model
                if LLM_PROXY_SETTINGS.is_reasoning_model
                else AGENT_SETTINGS.max_iterations
            ),
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
        return message_list["messages"]

    async def arun_agent_with_input(
        self, user_message: str, debug: Optional[bool] = False
    ) -> str:
        """Evaluates user input if debug print stream of messages in an asynchronus manner.
        The debug flags prints the execution trail of the agent
        The return parameter contains the execution trail"""

        LOGGER.info(
            "Running agent asynchronously with user message: %s",
            user_message.replace("\n", ""),
        )

        input_object = {"messages": [("user", user_message)]}

        config_object = {
            "recursion_limit": (
                AGENT_SETTINGS.max_iterations_reasoning_model
                if LLM_PROXY_SETTINGS.is_reasoning_model
                else AGENT_SETTINGS.max_iterations
            ),
        }

        run_start_time = time.perf_counter()

        message_list: list[BaseMessage] = []

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
        return message_list["messages"]

    def _post_process_agent_run(
        self, execution_messages: list[BaseMessage], run_time: float
    ) -> str:
        """Gather run information and extract final response
        The debug flags prints the execution trail of the agent
        The return parameter contains the execution trail"""

        # Set the final agent message as the response from the run
        self.run_data.final_output = self._extract_after_final_answer(
            execution_messages[-1].content
        )
        self.run_data.excecution_time_seconds = round(run_time, 3)

        for message in execution_messages:
            if isinstance(message, AIMessage):
                LLM_PROXY.increment_call_count()
                if message.additional_kwargs.get("tool_calls"):
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

        LLM_PROXY.update_llm_usage(execution_messages[-1])
        self.run_data.llm_call_count = LLM_PROXY.get_call_count()
        self.run_data.tokens_consumed = LLM_PROXY.get_token_usage()
        LLM_PROXY.reset_usage()

    def get_execution_data(self) -> AgentRun:
        """Help function for getting execution metadata"""
        return self.run_data

    def _extract_after_final_answer(self, text: str) -> str:
        """Extracts the final answer from the text after 'Final Answer:'."""
        match = re.search(
            r"(?:^|\n)\s*(?:#{1,6}\s*)?(?:\*\*)?\s*final answer\s*:?\s*(.*)",
            text,
            re.IGNORECASE | re.DOTALL,
        )

        final_answer = match.group(1).strip() if match else text.strip()

        # Remove trailing indicator for task completion
        final_answer = re.sub(
            r"\s*Task (?:done|complete)\.?\s*$", "", final_answer, flags=re.IGNORECASE
        ).strip()

        return final_answer
