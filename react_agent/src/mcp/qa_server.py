"""MCP Server for QA Tools"""

from mcp.server.fastmcp import FastMCP

from react_agent.src.agent_tools.sap_help_searcher import SapHelpSearcher
from react_agent.src.agent_tools.troubleshooting_searcher import TroubleshootingSearcher
from react_agent.src.config.system_parameters import QAToolsServerSettings
from react_agent.src.util.logger import LoggerSingleton

if __name__ == "__main__":
    settings = QAToolsServerSettings()
    logger = LoggerSingleton.get_logger(settings.name)

    mcp = FastMCP(
        name=settings.name,
        port=settings.port,
        host=settings.host,
    )

    tool_list = [SapHelpSearcher(), TroubleshootingSearcher()]

    for tool in tool_list:
        mcp.add_tool(
            tool._run,
            name=tool.name,
            description=tool.description,
        )

    logger.debug(
        "MCP Server %s starting with tools: %s",
        mcp.name,
        " ".join(tool.name for tool in tool_list),
    )
    mcp.run(transport=settings.transport)
