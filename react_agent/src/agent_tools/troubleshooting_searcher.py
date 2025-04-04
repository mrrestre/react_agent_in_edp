from typing import Type

from pydantic import BaseModel, Field

from langchain.tools.base import BaseTool

from react_agent.src.util.long_term_mem_manager import (
    PostgresMemoryManager,
    InMemoryManager,
)
from react_agent.src.scripts import (
    load_troubleshooting_postgres,
    load_troubleshooting_memory,
)

from react_agent.src.config.system_parameters import TROUBLESHOOTING_SEARCH


class TroubleshootingInputModel(BaseModel):
    """Input schema for the searching in long term memories about troubleshooting."""

    query: str = Field(
        ...,
        description="Query strings delimited by space. Provide one or more technical object names, if possible",
    )


class TroubleshootingSearcher(BaseTool):
    """Tool for searching domain specific knowledge from long term memory"""

    name: str = TROUBLESHOOTING_SEARCH.get("NAME")
    description: str = TROUBLESHOOTING_SEARCH.get("DESCRIPTION")
    args_schema: Type[BaseModel] = TroubleshootingInputModel

    def _run(self, query: str) -> str:
        """Search for most fitting memories to query in memory store"""
        if TROUBLESHOOTING_SEARCH.get("USE_IN_MEMORY_STORE"):
            mem_manager = InMemoryManager()
            load_troubleshooting_memory.load_memories(mem_manager)
        else:
            mem_manager = PostgresMemoryManager()
            load_troubleshooting_postgres.load_memories(mem_manager)

        return mem_manager.search_memories(
            query=query, limit=TROUBLESHOOTING_SEARCH.get("MEMORIES_LIMIT")
        )
