from langgraph.store.memory import InMemoryStore

from react_agent.src.util.embeddings_proxy import EmbeeddingProxy


class LongTermMemoryManager:
    def __init__(self, embedings_proxy: EmbeeddingProxy):
        self.store = InMemoryStore(
            index={"embed": embedings_proxy.embedding_model, "dims": 1536}
        )
        self.namespace = ("agent", "troubleshooting")

    def add_memory(self, memory_title: str, memory_text: str) -> None:
        self.store.put(
            namespace=self.namespace, key=memory_title, value={"text": memory_text}
        )

    def search_memory(self, query: str):
        # Find memories about food preferences
        memories = self.store.search(self.namespace, query=query, limit=5)

        for memory in memories:
            print(f'Memory: {memory.value["text"]} (similarity: {memory.score})')
