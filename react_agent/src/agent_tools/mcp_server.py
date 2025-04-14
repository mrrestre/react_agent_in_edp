from mcp.server.fastmcp import FastMCP

from react_agent.src.agent_tools.master_data_getter import MasterDataGetter
from react_agent.src.agent_tools.sap_help_searcher import SapHelpSearcher
from react_agent.src.agent_tools.troubleshooting_searcher import TroubleshootingSearcher
from react_agent.src.agent_tools.source_code_lookup import SourceCodeMethodLookup

mcp = FastMCP("ReAct-Tools")

tool_list = [SapHelpSearcher(), TroubleshootingSearcher(), SourceCodeMethodLookup()]

for tool in tool_list:
    mcp.add_tool(
        tool._run,
        name=tool.name,
        description=tool.description,
    )

if __name__ == "__main__":
    mcp.run(transport="sse")
