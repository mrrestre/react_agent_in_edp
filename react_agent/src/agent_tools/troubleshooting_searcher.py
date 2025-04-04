from typing import Type

from pydantic import BaseModel, Field

from langchain.tools.base import BaseTool

from react_agent.src.util.long_term_mem_manager import LongTermMemoryManager
from react_agent.src.scripts.load_troubleshooting import (
    load_memories,
)

MEMORIES_LIMIT = 2
TOOL_NAME = "search_memories"
TOOL_DESCR = """Returns eInvoicing domain specific knowledge related to the query string,
such as troubleshooting information, or details on Application Responses, 
Invoice Responses, Message Level Responses"""


class TroubleshootingInputModel(BaseModel):
    """Input schema for the searching in long term memories about troubleshooting."""

    query: str = Field(
        ...,
        description="Query strings delimited by space. Provide one or more technical object names, if possible",
    )


class TroubleshootingSearcher(BaseTool):
    """Tool for searching domain specific knowledge from long term memory"""

    name: str = TOOL_NAME
    description: str = TOOL_DESCR
    args_schema: Type[BaseModel] = TroubleshootingInputModel

    def _run(self, query: str) -> str:
        """Search for most fitting memories to query in memory store"""
        mem_manager = LongTermMemoryManager()

        load_memories(mem_manager)

        return mem_manager.search_memories(query=query, limit=MEMORIES_LIMIT)
