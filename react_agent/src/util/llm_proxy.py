"""LLM proxy for invoking language models and tracking usage."""

from typing import Optional, Type

import redis

from gen_ai_hub.proxy.langchain.init_models import init_llm
from gen_ai_hub.proxy.langchain.google_vertexai import (
    init_chat_model as google_vertexai_init_chat_model,
)
from gen_ai_hub.proxy.langchain.openai import init_chat_model as openai_init_chat_model

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from pydantic import BaseModel
from tiktoken import encoding_for_model
import tiktoken

from react_agent.src.config.system_parameters import LlmProxySettings
from react_agent.src.util.logger import LoggerSingleton

# -------------------------------------------------------------------
# Global Redis client (adjust host/port/db as needed)
_redis = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
# -------------------------------------------------------------------

LLM_PROXY_SETTINGS = LlmProxySettings()
LOGGER = LoggerSingleton.get_logger(LLM_PROXY_SETTINGS.logger_name)


class TokenConsumption(BaseModel):
    """Token consumption statistics for LLM usage."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    def pretty_print(self) -> None:
        """Print the token consumption statistics."""
        print("Token Consumption Statistics")
        print(f"  Input Tokens: {self.input_tokens}")
        print(f"  Output Tokens: {self.output_tokens}")
        print(f"  Total Tokens: {self.total_tokens}")


class SupportedModels(BaseModel):
    """Supported models for LLM invocation."""

    open_ai: list[str] = ["gpt-4o", "gpt-4o-mini"]
    open_ai_not_in_sdk: list[str] = ["gpt-4.1"]

    gemini_not_in_sdk: list[str] = ["gemini-2.0-flash"]

    def get_all_models(self) -> list[str]:
        """Get all supported models."""
        return self.open_ai + self.open_ai_not_in_sdk + self.gemini_not_in_sdk


class LlmProxy:
    """Proxy class for LLM invocation and usage tracking."""

    def __init__(self):
        self._redis_key = "llm_usage"
        self.reset_usage()

        if LLM_PROXY_SETTINGS.model not in SupportedModels().get_all_models():
            raise ValueError(
                f"Model {LLM_PROXY_SETTINGS.model} is not supported. Supported models are: {SupportedModels().get_all_models()}"
            )
        else:
            self._used_model = LLM_PROXY_SETTINGS.model

        self._initiliaze_llm()

    def _initiliaze_llm(self) -> None:
        # For models from Google Vertex AI not yet supported by the sdk, a specific initialization function is needed
        if self._used_model in SupportedModels().gemini_not_in_sdk:
            self._llm = init_llm(
                self._used_model,
                max_tokens=LLM_PROXY_SETTINGS.max_output_tokens,
                temperature=LLM_PROXY_SETTINGS.temperature,
                init_func=google_vertexai_init_chat_model,
            )
        # For models from OpenAI not yet supported by the sdk, a specific initialization function is needed
        elif self._used_model in SupportedModels().open_ai_not_in_sdk:
            self._llm = init_llm(
                self._used_model,
                max_tokens=LLM_PROXY_SETTINGS.max_output_tokens,
                temperature=LLM_PROXY_SETTINGS.temperature,
                init_func=openai_init_chat_model,
            )
        else:
            self._llm = init_llm(
                self._used_model,
                max_tokens=LLM_PROXY_SETTINGS.max_output_tokens,
                temperature=LLM_PROXY_SETTINGS.temperature,
            )

    def invoke(self, input: str, config: Optional[RunnableConfig] = None) -> str:
        """Invoke the LLM with the given input and configuration."""
        LOGGER.info("Invoking LLM (%s)", self._used_model)
        input_tokens = self._num_tokens_from_string(input)
        if input_tokens >= LLM_PROXY_SETTINGS.max_input_tokens:
            raise RuntimeError(
                f"Too many input tokens: {input_tokens} > {LLM_PROXY_SETTINGS.max_input_tokens}"
            )
        result = self._llm.invoke(input, config=config)
        self.increment_call_count()
        self.update_llm_usage(result)
        return result.content

    def invoke_with_structured_output(
        self,
        input: str,
        output_type: Type[BaseModel],
        config: Optional[RunnableConfig] = None,
    ) -> BaseModel:
        """Invoke the LLM with structured output."""
        LOGGER.info("Invoking LLM (%s) with structured output", self._used_model)
        input_tokens = self._num_tokens_from_string(input)
        if input_tokens >= LLM_PROXY_SETTINGS.max_input_tokens:
            raise RuntimeError(
                f"Too many input tokens: {input_tokens} > {LLM_PROXY_SETTINGS.max_input_tokens}"
            )
        result = self._llm.invoke_with_structured_output(
            input, output_type, config=config
        )
        self.increment_call_count()
        self.update_llm_usage(result)
        return result.content

    def _num_tokens_from_string(self, text: str) -> int:
        """Calculate the number of tokens in a string using the model's encoding."""
        if self._used_model in SupportedModels().open_ai:
            encoding = encoding_for_model(self._used_model)
        else:
            # Other model don't have public tokenizer, so we use OpenAI's cl100k_base as an approximation
            encoding = tiktoken.get_encoding("cl100k_base")

        return len(encoding.encode(text))

    def update_llm_usage(self, result: AIMessage) -> None:
        """Update the token usage statistics in Redis."""
        if not (isinstance(result, AIMessage) and result.usage_metadata):
            return

        meta = result.usage_metadata

        # Increment counters in Redis
        _redis.hincrby(self._redis_key, "input_tokens", meta.get("input_tokens", 0))
        _redis.hincrby(self._redis_key, "output_tokens", meta.get("output_tokens", 0))
        _redis.hincrby(self._redis_key, "total_tokens", meta.get("total_tokens", 0))

    def increment_call_count(self) -> None:
        """Increment the call count for the LLM."""
        _redis.hincrby(self._redis_key, "call_count", 1)

    def get_call_count(self) -> int:
        """Get the number of times the LLM has been called."""
        return int(_redis.hget(self._redis_key, "call_count") or 0)

    def get_token_usage(self) -> TokenConsumption:
        """Get the token usage statistics."""
        data = _redis.hgetall(self._redis_key)
        return TokenConsumption(
            input_tokens=int(data.get("input_tokens", 0)),
            output_tokens=int(data.get("output_tokens", 0)),
            total_tokens=int(data.get("total_tokens", 0)),
        )

    def reset_usage(self) -> None:
        """
        Clears all usage counters for this model from Redis.
        Call this whenever you want to start counting from zero again.
        """
        _redis.delete(self._redis_key)

    def get_used_model(self) -> str:
        """Get the model currently in use."""
        return self._used_model

    def set_new_model(self, model: str) -> None:
        """Set the model to be used."""
        init_function = None
        if model not in SupportedModels().get_all_models():
            raise ValueError(
                f"Model {model} is not supported. Supported models are: {SupportedModels().get_all_models()}"
            )
        if model in SupportedModels().gemini_not_in_sdk:
            init_function = google_vertexai_init_chat_model

        self._used_model = model
        self.reset_usage()
        self._llm = init_llm(
            self._used_model,
            max_tokens=LLM_PROXY_SETTINGS.max_output_tokens,
            temperature=LLM_PROXY_SETTINGS.temperature,
            init_func=init_function,
        )


# module‑level singleton
LLM_PROXY = LlmProxy()
