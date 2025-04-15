"""Utility functions for managing long term memory"""

from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres import PostgresStore

from psycopg import Connection

from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings

from react_agent.src.config.system_parameters import MemoryManagerSettings

settings = MemoryManagerSettings()


class InMemoryManager:
    """Utility functions for managing long term memory in memory"""

    def __init__(self):
        embedding_model = OpenAIEmbeddings(proxy_model_name=settings.embedding_model)
        self.store = InMemoryStore(
            index={
                "embed": embedding_model,
                "dims": settings.dimensions,
            }
        )
        self.namespace = settings.namespace

    def add_memory(self, memory_title: str, memory_text: str) -> None:
        """Add memory to long term memory store"""
        self.store.put(
            namespace=self.namespace, key=memory_title, value={"text": memory_text}
        )

    def search_memories(self, query: str) -> str:
        """Search for most fitting memories to query in memory store"""
        memories = self.store.search(
            self.namespace,
            query=query,
            limit=settings.memories_to_retrieve,
        )
        memories_text = [memory.value["text"] for memory in memories]
        return "\n".join(memories_text)

    def is_memory_present(self, title: str) -> bool:
        """Check if memory is present in long term memory store"""
        return self.store.get(namespace=self.namespace, key=title)


class PostgresMemoryManager:
    """Utility functions for managing long term memory in postgres"""

    def __init__(self):
        embedding_model = OpenAIEmbeddings(proxy_model_name=settings.embedding_model)
        self.conn = Connection.connect(settings.postgres_conn_string, autocommit=True)
        self.store = PostgresStore(
            conn=self.conn,
            index={
                "embed": embedding_model,
                "dims": settings.dimensions,
                "fields": ["text"],
            },
        )
        self.store.setup()

        self.namespace = settings.namespace

    def add_memory(self, memory_title: str, memory_text: str) -> None:
        """Add memory to long term memory store"""
        self.store.put(
            namespace=self.namespace, key=memory_title, value={"text": memory_text}
        )

    def search_memories(self, query: str) -> str:
        """Search for most fitting memories to query in memory store"""
        memories = self.store.search(
            self.namespace,
            query=query,
            limit=settings.memories_to_retrieve,
        )
        memories_text = [memory.value["text"] for memory in memories]
        return "\n".join(memories_text)

    def is_memory_present(self, title: str) -> bool:
        """Check if memory is present in long term memory store"""
        return self.store.get(namespace=self.namespace, key=title)
