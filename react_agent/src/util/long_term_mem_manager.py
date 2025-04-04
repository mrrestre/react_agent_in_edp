from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres import PostgresStore

from psycopg import Connection

from react_agent.src.util.embeddings_proxy import (
    EmbeeddingProxy,
    SupportedEmbeddingModels,
)

POSTGRES_CONN_STRING = (
    "postgresql://react_agent:react_agent@localhost:5432/troubleshooting"
)
EMBEDDING_MODEL = SupportedEmbeddingModels.ADA_002
NAMESPACE = ("agent", "troubleshooting")


class InMemoryManager:
    def __init__(self):
        embeddings = EmbeeddingProxy(model=EMBEDDING_MODEL.model_name)
        self.store = InMemoryStore(
            index={
                "embed": embeddings.embedding_model,
                "dims": EMBEDDING_MODEL.dims,
            }
        )
        self.namespace = NAMESPACE

    def add_memory(self, memory_title: str, memory_text: str) -> None:
        self.store.put(
            namespace=self.namespace, key=memory_title, value={"text": memory_text}
        )

    def search_memories(self, query: str, limit: int) -> str:
        memories = self.store.search(self.namespace, query=query, limit=limit)
        memories_text = [memory.value["text"] for memory in memories]
        return "\n".join(memories_text)

    def is_memory_present(self, title: str) -> bool:
        return self.store.get(namespace=self.namespace, key=title)


class PostgresMemoryManager:
    def __init__(self):
        embeddings = EmbeeddingProxy(model=EMBEDDING_MODEL.model_name)
        self.conn = Connection.connect(POSTGRES_CONN_STRING, autocommit=True)
        self.store = PostgresStore(
            conn=self.conn,
            index={
                "embed": embeddings.embedding_model,
                "dims": EMBEDDING_MODEL.dims,
                "fields": ["text"],
            },
        )
        self.store.setup()

        self.namespace = NAMESPACE

    def add_memory(self, memory_title: str, memory_text: str) -> None:
        self.store.put(
            namespace=self.namespace, key=memory_title, value={"text": memory_text}
        )

    def search_memories(self, query: str, limit: int) -> str:
        memories = self.store.search(self.namespace, query=query, limit=limit)
        memories_text = [memory.value["text"] for memory in memories]
        return "\n".join(memories_text)

    def is_memory_present(self, title: str) -> bool:
        return self.store.get(namespace=self.namespace, key=title)
