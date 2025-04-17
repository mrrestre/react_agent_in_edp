"""Utility functions for managing long term memory"""

from typing import Literal, Tuple
from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres import PostgresStore

from psycopg import Connection

from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings

from react_agent.src.config.system_parameters import MemoryManagerSettings
from react_agent.src.util.logger import LoggerSingleton

SETTINGS = MemoryManagerSettings()
LOGGER = LoggerSingleton.get_logger(SETTINGS.logger_name)


class MemoryManager:
    """Utility functions for managing long term memory"""

    MEMORY_STORE_TYPES = Literal["Memory", "Postgres"]

    def __init__(
        self, memory_store_type: MEMORY_STORE_TYPES, namespace: Tuple[str, str]
    ):
        self.memory_type = memory_store_type

        embedding_model = OpenAIEmbeddings(proxy_model_name=SETTINGS.embedding_model)

        if self.memory_type == "Memory":
            self.store = InMemoryStore(
                index={
                    "embed": embedding_model,
                    "dims": SETTINGS.dimensions,
                }
            )
        elif self.memory_type == "Postgres":
            self.conn = Connection.connect(
                SETTINGS.postgres_conn_string, autocommit=True
            )
            self.store = PostgresStore(
                conn=self.conn,
                index={
                    "embed": embedding_model,
                    "dims": SETTINGS.dimensions,
                    "fields": ["text"],
                },
            )
            self.store.setup()
        else:
            raise ValueError(f"Unknown memory store type: {self.memory_type}")

        self.namespace = namespace

    def add_memory(self, memory_title: str, memory_content=dict) -> None:
        """Add memory to long term memory store"""
        self.store.put(namespace=self.namespace, key=memory_title, value=memory_content)

    def search_memories(self, query: str) -> list[dict]:
        """Search for most fitting memories to query in memory store"""
        LOGGER.info("Searching for most fitting memories for query: %s", query)
        return self.store.search(
            self.namespace,
            query=query,
            limit=SETTINGS.memories_to_retrieve,
        )

    def is_memory_present(self, title: str) -> bool:
        """Check if memory is present in long term memory store"""
        return self.store.get(namespace=self.namespace, key=title)
