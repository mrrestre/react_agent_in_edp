# from dotenv import load_dotenv
from typing import Any, Optional, Dict, Type
from enum import Enum

from gen_ai_hub.proxy.langchain import init_llm

from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage

from pydantic import BaseModel

from tiktoken import encoding_for_model

from react_agent.src.config.system_parameters import LLM_PROXY


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

        self.used_model = LLM_PROXY.get("MODEL")

        self.llm = init_llm(
            self.used_model,
            max_tokens=LLM_PROXY.get("MAX_OUTPUT_TOKENS"),
            temperature=LLM_PROXY.get("TEMPERATURE"),
        )

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
            input_tokens_count = self.num_tokens_from_string(input_prompt)
            if input_tokens_count < LLM_PROXY.get("MAX_INPUT_TOKENS"):
                self.call_count += 1
                result = self.llm.invoke(input_prompt, config=config)
                self._update_token_usage(result)
                return result.content
            else:
                raise RuntimeError(
                    f"Too many input tokens, input tokens: {input_tokens_count}, max allowed: {LLM_PROXY.get("MAX_INPUT_TOKENS")}"
                )

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
            input_tokens_count = self.num_tokens_from_string(input_prompt)
            if input_tokens_count < LLM_PROXY.get("MAX_INPUT_TOKENS"):
                self.call_count += 1
                result = self.llm.invoke_with_structured_output(
                    input_prompt, output_type, config=config
                )
                self._update_token_usage(result)
                return result.content
            else:
                raise RuntimeError(
                    f"Too many input tokens, input tokens: {input_tokens_count}, max allowed: {LLM_PROXY.get("MAX_INPUT_TOKENS")}"
                )

    def num_tokens_from_string(self, string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = encoding_for_model(self.used_model)
        num_tokens = len(encoding.encode(string))
        return num_tokens

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
