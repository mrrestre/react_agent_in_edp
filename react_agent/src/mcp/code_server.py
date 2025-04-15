"""MCP Server for Code Tools"""

from mcp.server.fastmcp import FastMCP

from react_agent.src.agent_tools.troubleshooting_searcher import TroubleshootingSearcher

from react_agent.src.config.system_parameters import CodingsToolsServerSettings
from react_agent.src.util.logger import LoggerSingleton

if __name__ == "__main__":
    settings = CodingsToolsServerSettings()
    logger = LoggerSingleton.get_logger(settings.name)

    mcp = FastMCP(
        name=settings.name,
        port=settings.port,
        host=settings.host,
    )

    tool_list = [TroubleshootingSearcher()]

    for tool in tool_list:
        mcp.add_tool(
            tool._run,
            name=tool.name,
            description=tool.description,
        )

    logger.debug("MCP Server %s starting", mcp.name)
    mcp.run(transport="sse")
