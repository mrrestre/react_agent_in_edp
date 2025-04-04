from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres import PostgresStore

from psycopg import Connection

from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings

from react_agent.src.config.system_parameters import MEMORY_MANAGER


class InMemoryManager:
    def __init__(self):
        embedding_model = OpenAIEmbeddings(
            proxy_model_name=MEMORY_MANAGER.get("EMBEDDING_MODEL")
        )
        self.store = InMemoryStore(
            index={
                "embed": embedding_model,
                "dims": MEMORY_MANAGER.get("DIMENSIONS"),
            }
        )
        self.namespace = MEMORY_MANAGER.get("NAMESPACE")

    def add_memory(self, memory_title: str, memory_text: str) -> None:
        self.store.put(
            namespace=self.namespace, key=memory_title, value={"text": memory_text}
        )

    def search_memories(self, query: str) -> str:
        memories = self.store.search(
            self.namespace,
            query=query,
            limit=MEMORY_MANAGER.get("MEMORIES_TO_RETRIEVE"),
        )
        memories_text = [memory.value["text"] for memory in memories]
        return "\n".join(memories_text)

    def is_memory_present(self, title: str) -> bool:
        return self.store.get(namespace=self.namespace, key=title)


class PostgresMemoryManager:
    def __init__(self):
        embedding_model = OpenAIEmbeddings(
            proxy_model_name=MEMORY_MANAGER.get("EMBEDDING_MODEL")
        )
        self.conn = Connection.connect(
            MEMORY_MANAGER.get("POSTGRES_CONN_STRING"), autocommit=True
        )
        self.store = PostgresStore(
            conn=self.conn,
            index={
                "embed": embedding_model,
                "dims": MEMORY_MANAGER.get("DIMENSIONS"),
                "fields": ["text"],
            },
        )
        self.store.setup()

        self.namespace = MEMORY_MANAGER.get("NAMESPACE")

    def add_memory(self, memory_title: str, memory_text: str) -> None:
        self.store.put(
            namespace=self.namespace, key=memory_title, value={"text": memory_text}
        )

    def search_memories(self, query: str) -> str:
        memories = self.store.search(
            self.namespace,
            query=query,
            limit=MEMORY_MANAGER.get("MEMORIES_TO_RETRIEVE"),
        )
        memories_text = [memory.value["text"] for memory in memories]
        return "\n".join(memories_text)

    def is_memory_present(self, title: str) -> bool:
        return self.store.get(namespace=self.namespace, key=title)
