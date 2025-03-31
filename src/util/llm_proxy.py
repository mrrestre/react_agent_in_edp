# from dotenv import load_dotenv
from typing import Optional
from enum import Enum

from gen_ai_hub.proxy.langchain import init_llm

from langchain_core.language_models import BaseLanguageModel

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


class LLMProxy:
    """
    Singleton class to manage the initialization and invocation of a language model proxy.
    """

    _instance = None

    def __new__(
        cls,
        model: Optional[SupportedLLMs] = DEFAULT_LLM,
        max_tokens: Optional[int] = DEFAULT_MAX_TOKENS,
    ):
        if cls._instance is None:
            cls._instance = super(LLMProxy, cls).__new__(cls)
            cls._instance._initialize(
                model or DEFAULT_LLM, max_tokens or DEFAULT_MAX_TOKENS
            )
        return cls._instance

    def _initialize(self, model: SupportedLLMs, max_tokens: int):
        """Initialize the model only once."""
        if SupportedLLMs.has_value(model.value):
            self.llm = init_llm(model.value, max_tokens)
        else:
            raise ValueError("Invalid LLM model")

    def invoke(self, prompt: str) -> str:
        """Invoke the LLM with the given text."""
        if self.llm is None:
            raise RuntimeError("LLM proxy is not initialized")
        else:
            return self.llm.invoke(prompt)

    def get_llm(self) -> BaseLanguageModel:
        """Get the initialized LLM instance."""
        if self.llm is None:
            raise RuntimeError("LLM proxy is not initialized")
        else:
            return self.llm

    def invoke_with_output_model(self, output_model: BaseModel, prompt):
        """Invoke the LLM with the given text and return the structured output."""
        if self.llm is None:
            raise RuntimeError("LLM proxy is not initialized")
        else:
            structured_llm = self.llm.with_structured_output(output_model)
            return structured_llm.invoke(prompt)
