from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client


class EmbeeddingProxy:
    def __init__(self):
        self.embedding_model = OpenAIEmbeddings(
            proxy_model_name="text-embedding-ada-002"
        )

    def embed_text(self, text: str):
        return self.embedding_model.embed_query(text=text)
