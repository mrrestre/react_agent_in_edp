from typing import Any, Optional, Dict, Type
from enum import Enum

from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings

DEFAULT_MODEL = "text-embedding-ada-002"


class SupportedEmbeddingModels(Enum):
    """Models that are supported by the emebedding proxy"""

    ADA_002 = ("text-embedding-ada-002", 1536)

    def __init__(self, model_name: str, dims: int):
        self._model_name = model_name
        self._dims = dims

    @property
    def model_name(self):
        return self._model_name

    @property
    def dims(self):
        return self._dims

    @classmethod
    def has_value(cls, value):
        """Helper method to ensure model is supported"""
        return any(value == member.model_name for member in cls)


class EmbeeddingProxy:
    """
    Singleton class to manage the initialization and invocation of a language model proxy.
    """

    _instance: Optional["EmbeeddingProxy"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "EmbeeddingProxy":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model: Optional[str] = DEFAULT_MODEL):
        if hasattr(self, "_initialized"):  # prevent re-init
            return

        self.embedding_model = OpenAIEmbeddings(proxy_model_name=model)

        self._initialized = True

    def embed_text(self, text: str):
        """Returns an ambedding for the text in the input"""
        return self.embedding_model.embed_query(text=text)
