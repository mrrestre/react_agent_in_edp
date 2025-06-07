"""Defines constants for experiment folders and files used in the project."""

from enum import StrEnum


class ExperimentFolders(StrEnum):
    """Defines the folders used for experiments."""

    GPT_41 = "gpt-4.1"
    O3 = "o3"


class ExperimentFiles(StrEnum):
    """Defines the files used for experiments."""

    TRIAGE_LOCAL = "triage_local.json"

    ALL_TOOLS_LOCAL = "all_tools_local.json"
    ALL_TOOLS_LOCAL_NO_RANKING = "all_tools_local_no_ranking.json"

    TRIAGE_MCP = "triage_mcp.json"
    TRIAGE_MCP_SEQ_WEBSEARCH = "triage_mcp_seq_websearch.json"

    ALL_TOOLS_MCP_WEBSEARCH = "all_tools_mcp_websearch.json"
    ALL_TOOLS_MCP_SEQ = "all_tools_mcp_seq.json"
    ALL_TOOLS_MCP_SEQ_WEBSEARCH = "all_tools_mcp_seq_websearch.json"
    ALL_TOOLS_MCP_SEQ_WEBSEARCH_NO_RANKING = (
        "all_tools_mcp_seq_websearch_no_ranking.json"
    )

    NON_AGENTIC = "no_agent_no_tools.json"


# Price for 1,000 Model Tokens
ModelPricing = {
    "gpt-4.1": {"input": 0.00129, "output": 0.00494},
    "o3": {"input": 0.00610, "output": 0.02436},
    "anthropic--claude-3.5-sonnet": {"input": 0.00204, "output": 0.00988},
    # add other models as needed
}
