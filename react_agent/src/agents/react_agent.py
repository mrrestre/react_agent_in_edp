"""Description: ReAct Agent class to manage the React Agent and its tools."""

import json
import re
import time
from typing import Any, Optional
from langchain_core.messages import BaseMessage, AIMessage
from langchain.tools.base import BaseTool
from langgraph.prebuilt import create_react_agent

from react_agent.src.agents.models.react_agent_models import AgentRun, ToolCall
from react_agent.src.agents.react_agent_prompt_builder import create_sys_prompt
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
        is_judge_agent: Optional[bool] = False,
    ):
        self.run_data: AgentRun = AgentRun(
            model_used=LLM_PROXY_SETTINGS.model,
        )

        self.available_tools: list[BaseTool] = tool_list

        # Tool ranking are used if the agent is a judge agent or if the settings allow it
        self.system_prompt = create_sys_prompt(
            available_tools=self.available_tools,
            is_judge_agent=is_judge_agent,
            use_tool_rankings=AGENT_SETTINGS.use_tool_rankings or is_judge_agent,
        )

        self.agent = create_react_agent(
            model=LLM_PROXY._llm,
            tools=self.available_tools,
            prompt=self.system_prompt,
        )

    def get_system_prompt(self) -> str:
        """Get the system prompt used by the agent."""
        return self.system_prompt

    def get_agent_graph(self) -> bytes:
        """Get the agent's graph in Mermaid format."""
        return self.agent.get_graph().draw_mermaid_png()

    def run_agent_with_input(
        self, user_message: str, debug: Optional[bool] = False
    ) -> dict[str, Any]:
        """Evaluates user input if debug print the agent's stream of messages."""
        LOGGER.info(
            "Running agent synchronously with user message: %s",
            user_message.replace("\n", ""),
        )

        # In order to ensure that the LLM Proxy is reset and using the wanted model
        LLM_PROXY.set_new_model(LLM_PROXY_SETTINGS.model)

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
            for execution_trail in self.agent.stream(
                input=input_object, stream_mode="values", config=config_object
            ):
                message = execution_trail["messages"][-1]
                if isinstance(message, tuple):
                    print(message)
                else:
                    message.pretty_print()
        else:
            execution_trail = self.agent.invoke(
                input=input_object, config=config_object
            )
        run_end_time = time.perf_counter()

        self._post_process_agent_run(
            execution_trail["messages"], run_end_time - run_start_time
        )

        LOGGER.info("Agent final response: %s", self.run_data.final_output)
        return execution_trail

    async def arun_agent_with_input(
        self, user_message: str, debug: Optional[bool] = False
    ) -> dict[str, Any]:
        """Evaluates user input if debug print stream of messages in an asynchronus manner.
        The debug flags prints the execution trail of the agent
        The return parameter contains the execution trail"""

        LOGGER.info(
            "Running agent asynchronously with user message: %s",
            user_message.replace("\n", ""),
        )

        # In order to ensure that the LLM Proxy is reset and using the wanted model
        LLM_PROXY.set_new_model(LLM_PROXY_SETTINGS.model)

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
            async for execution_trail in self.agent.astream(
                input=input_object, stream_mode="values", config=config_object
            ):
                message = execution_trail["messages"][-1]
                if isinstance(message, tuple):
                    print(message)
                else:
                    message.pretty_print()

        else:
            execution_trail = await self.agent.ainvoke(
                input=input_object, config=config_object
            )
        run_end_time = time.perf_counter()

        self._post_process_agent_run(
            execution_trail["messages"], run_end_time - run_start_time
        )

        LOGGER.info("Agent final response: %s", self.run_data.final_output)
        return execution_trail

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
                # This is needed for vertex ai models
                elif message.additional_kwargs.get("function_call"):
                    function_call = message.additional_kwargs.get("function_call")
                    self.run_data.tools_used.append(
                        ToolCall(
                            tool_name=function_call.get("name"),
                            arguments=json.loads(function_call.get("arguments")),
                        )
                    )

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
