"""Tool for searching domain specific knowledge from long term memory"""

from typing import Type

from pydantic import BaseModel, Field

from langchain.tools.base import BaseTool

from react_agent.src.util.logger import LoggerSingleton
from react_agent.src.util.memory_manager import MemoryManager

from react_agent.src.config.system_parameters import TroubleshootingSearchSettings

TOOL_SETTINGS = TroubleshootingSearchSettings()
LOGGER = LoggerSingleton.get_logger(TOOL_SETTINGS.logger_name)


class TroubleshootingInputModel(BaseModel):
    """Input schema for the searching in long term memories about troubleshooting."""

    query: str = Field(
        ...,
        description=TOOL_SETTINGS.query_field_descr,
    )


class TroubleshootingSearcher(BaseTool):
    """Tool for searching domain specific knowledge from long term memory"""

    name: str = TOOL_SETTINGS.name
    description: str = TOOL_SETTINGS.description
    args_schema: Type[BaseModel] = TroubleshootingInputModel

    def _run(self, query: str) -> str:
        """Search for most fitting memories to query in memory store"""
        LOGGER.info("Searching for most fitting memories to query")

        mem_manager = MemoryManager(
            memory_store_type="Postgres", namespace=TOOL_SETTINGS.namespace
        )

        memories = mem_manager.search_memories(query=query)

        memories_text = [memory.value["text"] for memory in memories]
        return "\n".join(memories_text)
