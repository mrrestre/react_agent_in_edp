"""Tool for searching domain specific knowledge from long term memory"""

from typing import Type

from pydantic import BaseModel, Field

from langchain.tools.base import BaseTool

from react_agent.src.util.logger import LoggerSingleton
from react_agent.src.util.long_term_mem_manager import (
    PostgresMemoryManager,
    InMemoryManager,
)
from react_agent.src.scripts import (
    load_troubleshooting_postgres,
    load_troubleshooting_memory,
)

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
        if TOOL_SETTINGS.use_in_memory_store:
            LOGGER.info("Loading memories from in memory store")
            mem_manager = InMemoryManager()
            load_troubleshooting_memory.load_memories(mem_manager)
        else:
            LOGGER.info("Loading memories from postgres store")
            mem_manager = PostgresMemoryManager()
            load_troubleshooting_postgres.load_memories(mem_manager)

        return mem_manager.search_memories(query=query)
