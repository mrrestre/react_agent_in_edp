"""Utility functions for proxying LLMs"""

from typing import Optional, Dict, Type

from gen_ai_hub.proxy.langchain import init_llm

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage

from pydantic import BaseModel

from tiktoken import encoding_for_model

from react_agent.src.config.system_parameters import LlmProxySettings
from react_agent.src.util.logger import LoggerSingleton

LLM_PROXY_SETTINGS = LlmProxySettings()
LOGGER = LoggerSingleton.get_logger(LLM_PROXY_SETTINGS.logger_name)


class LLMProxy:
    """
    Manages the initialization and invocation of a language model proxy.
    Intended to be used as a singleton via the module-level instance.
    """

    def __init__(self):
        """
        Initializes the LLM proxy. This should only be called once
        during the module's loading.
        """
        self._used_model = LLM_PROXY_SETTINGS.model

        self._llm = init_llm(
            self._used_model,
            max_tokens=LLM_PROXY_SETTINGS.max_output_tokens,
            temperature=LLM_PROXY_SETTINGS.temperature,
        )

        self._token_usage: Dict[str, int] = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }
        self.call_count: int = 0

    def invoke(self, input: str, config: Optional[RunnableConfig] = None) -> str:
        """Invokes the underlying LLM and monitors token usage and call count."""
        LOGGER.info(
            "Invoking LLM (%s)",
            self._used_model,
        )

        input_tokens_count = self.num_tokens_from_string(input)
        if input_tokens_count < LLM_PROXY_SETTINGS.max_input_tokens:
            result = self._llm.invoke(input, config=config)
            self.update_llm_usage(result)
            return result.content
        else:
            raise RuntimeError(
                f"Too many input tokens, input tokens: {input_tokens_count}, max allowed: {LLM_PROXY_SETTINGS.max_input_tokens}"
            )

    def invoke_with_structured_output(
        self,
        input: str,
        output_type: Type[BaseModel],
        config: Optional[RunnableConfig] = None,
    ) -> BaseModel:
        """Invokes the LLM with structured output and monitors token usage and call count."""
        LOGGER.info(
            "Invoking LLM (%s) with input: %s and structured output",
            self._used_model,
            input,
        )

        input_tokens_count = self.num_tokens_from_string(input)
        if input_tokens_count < LLM_PROXY_SETTINGS.max_input_tokens:
            result = self._llm.invoke_with_structured_output(
                input, output_type, config=config
            )
            self.update_llm_usage(result)
            return result.content
        else:
            raise RuntimeError(
                f"Too many input tokens, input tokens: {input_tokens_count}, max allowed: {LLM_PROXY_SETTINGS.max_input_tokens}"
            )

    def num_tokens_from_string(self, string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = encoding_for_model(self._used_model)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def update_llm_usage(self, result: AIMessage) -> None:
        """Updates the token usage metrics based on the LLM result."""
        if isinstance(result, AIMessage) and result.usage_metadata:
            self.call_count += 1

            self._token_usage["input_tokens"] += result.usage_metadata.get(
                "input_tokens", 0
            )
            self._token_usage["output_tokens"] += result.usage_metadata.get(
                "output_tokens", 0
            )
            self._token_usage["total_tokens"] += result.usage_metadata.get(
                "total_tokens", 0
            )

    def get_token_usage(self) -> Dict[str, int]:
        """Returns the current token usage metrics."""
        return self._token_usage

    def get_call_count(self) -> int:
        """Returns the current call count."""
        return self.call_count

    def print_usage(self) -> None:
        """Prints the current call count and token usage."""
        print(f"Call Count: {self.call_count}")
        print(f"Token Usage: {self._token_usage}")

    def reset_call_count(self) -> None:
        """USE ONLY FOR UNIT TESTING - Resets the call count"""
        self.call_count = 0


# Create a single instance of LLMProxy when the module is imported
# This instance will be the de facto singleton
LLM_PROXY = LLMProxy()
