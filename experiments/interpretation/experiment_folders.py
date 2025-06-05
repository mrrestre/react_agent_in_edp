"""Defines constants for experiment folders and files used in the project."""

from enum import StrEnum


class ExperimentFolders(StrEnum):
    """Defines the folders used for experiments."""

    GPT_41 = "gpt-4.1"


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
