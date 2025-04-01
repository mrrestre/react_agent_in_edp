# from dotenv import load_dotenv
from typing import Any, Optional, Dict, Type, Union
from enum import Enum

from gen_ai_hub.proxy.langchain import init_llm

from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage

from pydantic import BaseModel


class SupportedLLMs(Enum):
    """LLMs that are supported by the LLMProxy"""

    GPT_4o = "gpt-4o"

    @classmethod
    def has_value(cls, value):
        """Helper method to ensure LLM is supoorted"""
        return value in cls._value2member_map_


DEFAULT_LLM = SupportedLLMs.GPT_4o
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TEMPERATURE = 0.05


class LLMProxy:
    """
    Singleton class to manage the initialization and invocation of a language model proxy.
    """

    _instance: Optional["LLMProxy"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "LLMProxy":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        model: Optional[str] = DEFAULT_LLM,
        max_tokens: Optional[int] = DEFAULT_MAX_TOKENS,
        temperature: Optional[float] = DEFAULT_TEMPERATURE,
    ):
        if hasattr(self, "_initialized"):  # prevent re-init
            return

        if SupportedLLMs.has_value(model.value):
            self.llm = init_llm(
                model.value, max_tokens=max_tokens, temperature=temperature
            )
        else:
            raise ValueError("Invalid LLM model")

        self.token_usage: Dict[str, int] = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }
        self.call_count: int = 0
        self._initialized = True

    def invoke(self, input_prompt: str, config: Optional[RunnableConfig] = None) -> str:
        """Invokes the underlying LLM and monitors token usage and call count."""
        if self.llm is None:
            raise RuntimeError("LLM proxy is not initialized")
        else:
            self.call_count += 1
            result = self.llm.invoke(input_prompt, config=config)
            self._update_token_usage(result)
            return result.content

    def invoke_with_structured_output(
        self,
        input_prompt: str,
        output_type: Type[BaseModel],
        config: Optional[RunnableConfig] = None,
    ) -> BaseModel:
        """Invokes the LLM with structured output and monitors token usage and call count."""
        if self.llm is None:
            raise RuntimeError("LLM proxy is not initialized")
        else:
            self.call_count += 1
            result = self.llm.invoke(input_prompt, config=config)
            self._update_token_usage(result)
            return self.llm.invoke_with_structured_output(
                input_prompt, output_type, config=config
            )

    def _update_token_usage(self, result: AIMessage) -> None:
        """Updates the token usage metrics based on the LLM result."""
        if isinstance(result, AIMessage) and result.usage_metadata:
            self.token_usage["input_tokens"] += result.usage_metadata["input_tokens"]
            self.token_usage["output_tokens"] += result.usage_metadata["output_tokens"]
            self.token_usage["total_tokens"] += result.usage_metadata["total_tokens"]

    def get_llm(self) -> BaseLanguageModel:
        """Get the initialized LLM instance."""
        if self.llm is None:
            raise RuntimeError("LLM proxy is not initialized")
        else:
            return self.llm

    def get_token_usage(self) -> Dict[str, int]:
        """Returns the current token usage metrics."""
        return self.token_usage

    def get_call_count(self) -> int:
        """Returns the current call count."""
        return self.call_count

    def print_usage(self) -> None:
        """Prints the current call count and token usage."""
        print(f"Call Count: {self.call_count}")
        print(f"Token Usage: {self.token_usage}")
