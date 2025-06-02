"""Configuration for the React Agent prompts and instructions"""

from langchain.prompts import PromptTemplate
from langchain.tools.base import BaseTool
from langchain_core.tools import StructuredTool

from react_agent.src.config.agent_prompts import ReactAgentPrompts, ToolRankingSettings
from react_agent.src.config.system_parameters import LlmProxySettings

RANKING_SETTINGS = ToolRankingSettings()
PROMPTS = ReactAgentPrompts()
LLM_PROXY_SETTINGS = LlmProxySettings()


def create_sys_prompt(
    available_tools: list[BaseTool],
    is_judge_agent: bool = False,
    use_tool_rankings: bool = True,
) -> str:
    """Create the system prompt for the agent."""

    if use_tool_rankings:
        tool_rankings = ""
        for tool in available_tools:
            if tool is not isinstance(tool, StructuredTool):
                continue
            if RANKING_SETTINGS.tool_rankings.get(tool.name):
                tool_rankings += f"Tool name: {tool.name}, Ranking: {RANKING_SETTINGS.tool_rankings.get(tool.name)}\n"
            elif RANKING_SETTINGS.mcp_tool_ranking.get(tool.name):
                tool_rankings += f"Tool name: {tool.name}, Ranking: {RANKING_SETTINGS.mcp_tool_ranking.get(tool.name)}\n"

        prompt_template = (
            PROMPTS.system_prompt_tool_rankings
            if not is_judge_agent
            else PROMPTS.system_prompt_judge_agent
        )

        return prompt_template.format(
            react_instructions=("\n").join(
                PROMPTS.reasoning_model_instructions
                if LLM_PROXY_SETTINGS.is_reasoning_model
                else PROMPTS.react_instructions
            ),
            tools=generate_tool_info_string(available_tools=available_tools),
            rules=("\n").join(PROMPTS.rules_tool_rankings),
            tool_rankings=tool_rankings,
        )
    else:
        return PROMPTS.system_prompt.format(
            react_instructions=("\n").join(
                PROMPTS.reasoning_model_instructions
                if LLM_PROXY_SETTINGS.is_reasoning_model
                else PROMPTS.react_instructions
            ),
            tools=generate_tool_info_string(available_tools=available_tools),
            rules=("\n").join(PROMPTS.rules_tool_memory),
        )


def generate_tool_info_string(available_tools: list[BaseTool]) -> str:
    """Generates a string containing tool names, arg schemas, and descriptions."""
    tool_strings = []
    for tool in available_tools:
        if isinstance(tool, StructuredTool):
            schema_props = tool.args_schema.get("properties")
        else:
            continue

        arg_components = ", ".join(
            f"{name}: {prop['type']}" for name, prop in schema_props.items()
        )

        tool_strings.append(
            f"- Tool Name: {tool.name}, Description: {tool.description}, Args: {arg_components}"
        )

    return "\n".join(tool_strings)
