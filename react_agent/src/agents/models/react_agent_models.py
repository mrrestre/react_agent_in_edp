"""Models for the react agent"""

from typing import Optional
from pydantic import BaseModel

from react_agent.src.util.llm_proxy import TokenConsumption


class ToolCall(BaseModel):
    """Schema for tool call properties"""

    tool_name: str
    arguments: Optional[dict[str, str]]


class AgentRun(BaseModel):
    """Schema for the agent run data."""

    final_output: str = ""
    tools_used: list[ToolCall] = []
    excecution_time_seconds: float = 0.0
    model_used: str = ""
    tokens_consumed: TokenConsumption = TokenConsumption()
    llm_call_count: int = 0

    def pretty_print(self):
        """Print excecution summary nicely"""
        print("Agent Run Summary")
        print("=" * 40)
        print(f"Final Output:\n{self.final_output}\n")
        print(f"Model Used:\n{self.model_used}\n")
        print(f"Execution Time: \n{self.excecution_time_seconds} seconds\n")
        self.tokens_consumed.pretty_print()
        print(f"\nLLM call count: {self.llm_call_count}\n")

        print("Tools Used:")
        if not self.tools_used:
            print("  None")
        else:
            for i, tool in enumerate(self.tools_used, start=1):
                print(f"  Tool #{i}:")
                print(f"    Name: {tool.tool_name}")
                print("    Arguments:")
                for arg_key, arg_value in tool.arguments.items():
                    print(f"      {arg_key}: {arg_value}")
        print("=" * 40)
