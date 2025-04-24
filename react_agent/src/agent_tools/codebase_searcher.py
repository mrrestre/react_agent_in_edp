"""Tool for searching domain specific knowledge from long term memory"""

from typing import Type

from pydantic import BaseModel, Field

from langchain.tools.base import BaseTool

from react_agent.src.config.system_parameters import CodebaseSearcherSettings
from react_agent.src.util.logger import LoggerSingleton
from react_agent.src.util.memory_manager import MemoryManager


TOOL_SETTINGS = CodebaseSearcherSettings()
LOGGER = LoggerSingleton.get_logger(TOOL_SETTINGS.logger_name)


class CodebaseSearcherInputModel(BaseModel):
    """Input schema for source_code_lookup"""

    query: str = Field(
        ...,
        description=TOOL_SETTINGS.query_field_descr,
    )


class CodebaseSearcher(BaseTool):
    """Tool for searching source code in ABAP codebase"""

    name: str = TOOL_SETTINGS.name
    description: str = TOOL_SETTINGS.description
    args_schema: Type[BaseModel] = CodebaseSearcherInputModel

    def _run(self, query: str) -> str:
        """Search for most fitting source code snippets to query in memory store"""
        LOGGER.info("Searching for most fitting memories to query")

        mem_manager = MemoryManager(
            memory_store_type="Postgres", namespace=TOOL_SETTINGS.namespace
        )

        memories = mem_manager.search_memories(query=query)

        response = ""
        for memory in memories:
            response += f"{memory.value['code']}\n"

        return response
