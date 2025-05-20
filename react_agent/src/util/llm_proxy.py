"""LLM proxy for invoking language models and tracking usage."""

from typing import Optional, Type

import redis

from gen_ai_hub.proxy.langchain import init_llm
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from pydantic import BaseModel
from tiktoken import encoding_for_model

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


class LlmProxy:
    """Proxy class for LLM invocation and usage tracking."""

    def __init__(self):
        self._used_model = LLM_PROXY_SETTINGS.model
        self.reset_usage()
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
        self.update_llm_usage(result)
        return result.content

    def _num_tokens_from_string(self, text: str) -> int:
        """Calculate the number of tokens in a string using the model's encoding."""
        encoding = encoding_for_model(self._used_model)
        return len(encoding.encode(text))

    def update_llm_usage(self, result: AIMessage) -> None:
        """Update the token usage statistics in Redis."""
        if not (isinstance(result, AIMessage) and result.usage_metadata):
            return

        meta = result.usage_metadata
        key = f"llm_usage:{self._used_model}"

        # Increment counters in Redis
        _redis.hincrby(key, "call_count", 1)
        _redis.hincrby(key, "input_tokens", meta.get("input_tokens", 0))
        _redis.hincrby(key, "output_tokens", meta.get("output_tokens", 0))
        _redis.hincrby(key, "total_tokens", meta.get("total_tokens", 0))

    def get_call_count(self) -> int:
        """Get the number of times the LLM has been called."""
        key = f"llm_usage:{self._used_model}"
        return int(_redis.hget(key, "call_count") or 0)

    def get_token_usage(self) -> TokenConsumption:
        """Get the token usage statistics."""
        key = f"llm_usage:{self._used_model}"
        data = _redis.hgetall(key)
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
        key = f"llm_usage:{self._used_model}"
        _redis.delete(key)

    def get_used_model(self) -> str:
        """Get the model currently in use."""
        return self._used_model

    def set_new_model(self, model: str) -> None:
        """Set the model to be used."""
        self._used_model = model
        self.reset_usage()
        self._llm = init_llm(
            self._used_model,
            max_tokens=LLM_PROXY_SETTINGS.max_output_tokens,
            temperature=LLM_PROXY_SETTINGS.temperature,
        )


# module‑level singleton
LLM_PROXY = LlmProxy()
