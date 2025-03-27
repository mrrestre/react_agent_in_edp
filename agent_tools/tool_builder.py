from langchain.tools import Tool

from agent_tools.i_agent_tool import IAgentTool


class ToolBuilder:

    @staticmethod
    def create_tool(tool: IAgentTool) -> Tool:
        """Define a tool from an IAgentTool instance.
        Uses the method, name, description, and args_schema attributes."""
        return Tool.from_function(
            func=tool.method,
            name=tool.name,
            description=tool.description,
            args_schema=tool.args_schema,
        )
