import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

from config import LLM_configs


class LlmProxy:
    def __init__(self):
        _ = load_dotenv()

        LLM_in_use = os.environ["LLM_IN_USE"]

        if LLM_in_use == LLM_configs.GEMINI_15_FLASH["name"]:
            self.llm = ChatGoogleGenerativeAI(
                model=LLM_configs.GEMINI_15_FLASH["name"],
                google_api_key=os.getenv(LLM_configs.GEMINI_15_FLASH["key_name"]),
            )
        else:
            raise ValueError("Invalid LLM model")

    def invoke(self, text) -> str:
        return self.llm.invoke(text)
