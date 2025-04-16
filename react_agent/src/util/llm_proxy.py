"""Utility functions for proxying LLMs"""

from typing import Any, Optional, Dict, Type

from gen_ai_hub.proxy.langchain import init_llm

from langchain_core.language_models import BaseLanguageModel
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
    Singleton class to manage the initialization and invocation of a language model proxy.
    """

    _instance: Optional["LLMProxy"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "LLMProxy":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):  # prevent re-init
            return

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
        self._initialized = True

    def invoke(self, input: str, config: Optional[RunnableConfig] = None) -> str:
        """Invokes the underlying LLM and monitors token usage and call count."""
        LOGGER.info(
            "Invoking LLM (%s)",
            self._used_model,
        )
        if self._llm is None:
            raise RuntimeError("LLM proxy is not initialized")
        else:
            input_tokens_count = self.num_tokens_from_string(input)
            if input_tokens_count < LLM_PROXY_SETTINGS.max_input_tokens:
                self.call_count += 1
                result = self._llm.invoke(input, config=config)
                self._update_token_usage(result)
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
        if self._llm is None:
            raise RuntimeError("LLM proxy is not initialized")
        else:
            input_tokens_count = self.num_tokens_from_string(input)
            if input_tokens_count < LLM_PROXY_SETTINGS.max_input_tokens:
                self.call_count += 1
                result = self._llm.invoke_with_structured_output(
                    input, output_type, config=config
                )
                self._update_token_usage(result)
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

    def _update_token_usage(self, result: AIMessage) -> None:
        """Updates the token usage metrics based on the LLM result."""
        if isinstance(result, AIMessage) and result.usage_metadata:
            self._token_usage["input_tokens"] += result.usage_metadata["input_tokens"]
            self._token_usage["output_tokens"] += result.usage_metadata["output_tokens"]
            self._token_usage["total_tokens"] += result.usage_metadata["total_tokens"]

    def get_llm(self) -> BaseLanguageModel:
        """Get the initialized LLM instance."""
        if self._llm is None:
            raise RuntimeError("LLM proxy is not initialized")
        else:
            return self._llm

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
