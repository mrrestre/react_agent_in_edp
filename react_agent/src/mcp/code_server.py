"""MCP Server for Code Tools"""

from mcp.server.fastmcp import FastMCP

from react_agent.src.agent_tools.database_entries_retriever import DBEntriesRetriever
from react_agent.src.agent_tools.source_code_retriever import SourceCodeRetriever
from react_agent.src.agent_tools.codebase_searcher import CodebaseSearcher

from react_agent.src.config.system_parameters import CodingToolsServerSettings
from react_agent.src.util.logger import LoggerSingleton

if __name__ == "__main__":
    settings = CodingToolsServerSettings()
    logger = LoggerSingleton.get_logger(settings.name)

    mcp = FastMCP(
        name=settings.name,
        port=settings.port,
        host=settings.host,
    )

    tool_list = [SourceCodeRetriever(), CodebaseSearcher(), DBEntriesRetriever()]

    for tool in tool_list:
        mcp.add_tool(
            tool._run,
            name=tool.name,
            description=tool.description,
        )
    logger.info(
        "MCP Server %s starting with tools: %s",
        mcp.name,
        " ".join(tool.name for tool in tool_list),
    )

    mcp.run(transport=settings.transport)
