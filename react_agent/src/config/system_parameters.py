"""Configuration parameters for agent, tools and proxies"""

from enum import Enum, StrEnum
import logging
from typing import Any, Dict, List, Tuple

from pydantic_settings import BaseSettings

from react_agent.src.agent_tools.models.documentation_retriever_models import (
    ChatSlotCloudType,
)

# --------------- Agent Tools --------------- #


class SapHelpToolSettings(BaseSettings):
    """Settings for SAP Help Tool"""

    logger_name: str = "SAP Help Tool"

    # Tool Description
    name: str = "sap_help_lookup"
    description: str = (
        "Returns summaries of SAP Help articles based on keyword prompts, focusing on official feature descriptions and configuration documentation from SAP’s public documentation site."
    )

    # Input model description
    query_field_descr: str = (
        "A query composed of up to 5 words, each representing a technical object name. Words should be space-separated."
    )
    # Tool specifics
    product_name: str = "SAP_S4HANA_CLOUD"
    language: str = "en-US"
    article_state: str = "PRODUCTION"
    top_n_articles: int = 10
    max_article_size: int = 800 * 1024  # 800 KB
    max_num_words: int = 1000
    summarization_prompt: str = """## Role
You are an expert in Electronic Document Processing, with deep domain knowledge in:
- SAP Document and Reporting Compliance
- Peppol, UBL, and other eInvoicing standards
- SAP S/4HANA configuration and technical architecture

## Task
Your job is to summarize **the technical content** of the following markdown article(s), focusing on how they address the user's specific query.

### User Query:
"{query}"

### Instructions:
- Summarize in **no more than {max_num_words} words**
- Focus on **how the markdown content answers or relates to the query**
- Emphasize **technical elements**:
    - SAP transaction codes
    - Configuration paths or steps
    - Technical objects (e.g., function modules, tables, BAPIs, SAP Notes)
- When appropriate, use **bullet points** for:
    - Configuration steps
    - Key SAP terms or components
    - Implementation hints

### Synthesis Guidelines:
- If multiple articles are present:
    - Combine overlapping information
    - Eliminate redundancy
- Avoid generalities or unrelated info
- Prefer **concrete mappings** between content and the query

### Input Markdown:
```markdown
{markdown_content}
```"""


class TroubleshootingSearchSettings(BaseSettings):
    """Settings for Troubleshooting Search"""

    logger_name: str = "Troubleshooting Search Tool"

    # Tool Description
    name: str = "edp_troubleshooting_search"
    description: str = """Retrieves troubleshooting information related to the Electronic Document Processing (EDP) using semantic similarity.
Returns chunks of potentially relevant diagnostic guidance and known issue resolutions."""

    # Input model description
    query_field_descr: str = (
        "Query composed of one or more keywords related to the question. Separate keywords with spaces."
    )

    # Tool specifics
    namespace: Tuple[str, str] = ("agent", "troubleshooting")


class DocumentationRetrieverSettings(BaseSettings):
    """Settings for Documentation Retriever"""

    logger_name: str = "Documentation Retriever Tool"

    # Tool Description
    name: str = "sap_documentation_summary"
    description: str = (
        "Summarizes SAP documentation content from multiple trusted sources, including official guides, internal documentation, and expert references, to provide accurate and reliable answers to SAP-related queries."
    )

    # Input model description
    query_field_descr: str = (
        "Short, focused description of a specific concept, feature, configuration, or question you want answered using official documentation sources."
    )

    # Tool specifics
    search_service_relative_path: str = "/api/v1/search"
    oauth_token_path: str = "/oauth2/token?grant_type=client_credentials"
    request_timeout: int = 60  # Timeout for the request in seconds

    # Model parameters
    prompt_introduction: str = (
        "You are a helpful assistant. You are given information on a product named Document and Reporting Compliance, cloud edition. The product is also known as\n- DRC\n- DRCce\n- Foundation Layer\n- Communication Layer\n"
    )
    default_cloud_type: ChatSlotCloudType = ChatSlotCloudType.PUBLIC_CLOUD
    collection_id: str = "70386ab8-eeac-452c-b2e6-cac902ca451c"
    max_chunk_count_collection: int = 5
    max_chunk_count_sap_help: int = 3


class SourceCodeRetrieverSettings(BaseSettings):
    """Settings for Source Code Retriever"""

    logger_name: str = "Source Code Retriever Tool (XCO)"

    # Tool Description
    name: str = "external_class_code_lookup"
    description: str = """This is a fallback tool. Do not use unless the class is known to be missing from the pre-indexed dataset.
Retrieves the full source code of an ABAP class by querying an external repository.
Use this tool only when the target class is not found in the pre-indexed codebase or when previous method-specific tools return no results.
Returns the complete class source as plain text."""

    # Input model description
    class_name_field_descr: str = "The exact name of an ABAP class"


class DBEntriesRetrieverSettings(BaseSettings):
    """Settings for Database Entries Retriever"""

    logger_name: str = "Database Entries Retriever Tool"

    # Tool Description
    name: str = "sap_database_entry_lookup"
    description: str = """Retrieves database entries directly from an SAP system table.
Requires the exact name of the database table (e.g., BKPF, MARA).
Returns the matching entries as structured JSON containing database entries."""

    # Input model description
    class_name_field_descr: str = "The exact name of an SAP-System database name"

    # Tool specifics
    max_entries: int = 100


class CodebaseSearcherSettings(BaseSettings):
    """Settings for Source Code Lookup"""

    logger_name: str = "Codebase Search Tool"

    # Tool Description
    name: str = "abap_method_codebase_search"
    description: str = """Tool for retrieving ABAP methods relevant to a natural language query, based on semantic similarity with method descriptions in a pre-indexed codebase.
Returns a ranked list of matching methods with following attributes: class name, method name, parent class, implemented interfaces, method implementation.
This is the preferred tool for finding code snippets or implementations.
Use this before any full-class or external code retrieval tools.
Repeated calls with different inputs are valid and may return distinct results."""

    # Input model description
    query_field_descr: str = (
        "A query consisting of at most five keywords related to the code you're looking for, separated by spaces."
    )

    # Tool specifics
    namespace: Tuple[str, str] = ("agent", "source_code")


# --------------- Agent --------------- #


class AgentSettings(BaseSettings):
    """Settings for the Main Agent"""

    logger_name: str = "ReAct Agent"
    max_iterations: int = 10
    max_iterations_reasoning_model: int = (
        40  # For reasoning models more steps are needed
    )
    use_tool_rankings: bool = True


# --------------- MCP Servers --------------- #


class QAToolsServerSettings(BaseSettings):
    """Settings for QuestionAnsweringToolsServer"""

    name: str = "QuestionAnsweringTools"
    port: int = 8000
    host: str = "0.0.0.0"
    transport: str = "sse"


class CodingToolsServerSettings(BaseSettings):
    """Settings for CodingToolsServer"""

    name: str = "CodingTools"
    port: int = 8001
    host: str = "0.0.0.0"
    transport: str = "sse"


# --------------- Utils --------------- #


class CodeSummarizerSettings(BaseSettings):
    """Settings for the Code Summarizer"""

    logger_name: str = "Code Summarizer"
    prompt_template: str = """As an expert in ABAP development, provide a concise summary (2-3 sentences) of the primary purpose and key functionality of the following ABAP method.
Take into account the description of the class as context.
ABAP Method Source Code:
```abap
{source_code}
```"""


class ABAPRepositorySettings(BaseSettings):
    """Settings for the ABAP Repository"""

    logger_name: str = "ABAP Repository"


class LoggerSettings(BaseSettings):
    """Settings for the Logger"""

    filename: str = "./logs/logs.txt"
    level: int = logging.INFO
    format: str = "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"


class LlmProxySettings(BaseSettings):
    """Settings for the LLM Proxy"""

    logger_name: str = "LLM Proxy"
    model: str = (
        "o3"  # gemini-2.0-flash / gpt-4o / gpt-4.1 / o3 / anthropic--claude-3.5-sonnet
    )
    is_reasoning_model: bool = True if model in ["o3"] else False
    max_output_tokens: int = 6000
    temperature: float = 0.05
    max_input_tokens: int = 60000 if is_reasoning_model else 20000


class MemoryManagerSettings(BaseSettings):
    """Settings for the Memory Manager"""

    logger_name: str = "Memory Manager"
    embedding_model: str = "text-embedding-ada-002"
    dimensions: int = 1536
    postgres_conn_string: str = (
        "postgresql://react_agent:react_agent@localhost:5432/troubleshooting"
    )
    memories_to_retrieve: int = 8


class TriageSettings(BaseSettings):
    """Settings for the Triage component"""

    logger_name: str = "Triage"
    sys_prompt: str = """## Role
You are a Triage Agent responsible for classifying user questions into the most appropriate category for downstream processing.

## Task
Analyze the user question carefully and assign it to **exactly one** of the following categories:
{categories}

## Guidelines
- Base your decision strictly on the nature of the question.
- Focus on **what kind of processing** the question requires (e.g., factual lookup vs. investigation).
- Always choose the **single most fitting** category, even if the question appears ambiguous.

## Category Definitions
{triage_rules}

## Output Format
- Respond only with a valid JSON object matching the schema.
- Populate the fields with real values from the user input.
- **Do NOT** return the schema structure or its definitions.
- The final output must look like a fully populated object.

## Example Outputs
{examples}
"""

    class Categories(str, Enum):
        """Possible categories from the incomming query"""

        KNOWLEDGE_QA = "Knowledge-QA"
        CONFIG_RCA = "Config-RCA"
        ALL = "All Tools"

    instructions: List[Dict[str, str]] = [
        {
            "category": Categories.KNOWLEDGE_QA,
            "description": "General or technical questions that can be answered using existing knowledge, documentation, or expert understanding. These typically ask for facts, explanations, best practices, or implementation guidance.",
        },
        {
            "category": Categories.CONFIG_RCA,
            "description": "Questions that require root cause analysis or system-specific investigation. These often involve unexpected behavior, configuration analysis, or tracing logic (e.g., mappings, process flows, custom enhancements).",
        },
    ]
    examples: List[Dict[str, str]] = [
        {
            "question": "As a Public Cloud customer in Spain, can I extend an existing eDocument customer invoice Process?",
            "category": Categories.KNOWLEDGE_QA,
        },
        {
            "question": "Explain how 'Payment Terms' is mapped. Start with 'map_invoice1'.",
            "category": Categories.CONFIG_RCA,
        },
        {
            "question": "I want to extend the standard E-Mail sent to customers, generate a sample code to enhance the E-Mail attachmentby adding additional file of type PDF.",
            "category": Categories.KNOWLEDGE_QA,
        },
        {
            "question": "Explain how 'Payment Terms' is mapped. Start with 'map_invoice1'.",
            "category": Categories.CONFIG_RCA,
        },
    ]
    response_schema: Dict[str, Any] = {
        "title": "Triage Output",
        "type": "object",
        "properties": {
            "user_query": {
                "type": "string",
                "description": "The original unmodified user question",
            },
            "category": {
                "type": "string",
                "description": "The category choosen by the triage",
            },
        },
    }


class ToolsFabricSettings(BaseSettings):
    """Settings for the Tools Fabric"""

    logger_name: str = "Tools Fabric"

    # MCP DuckDuckGo Settings
    include_duckduckgo: bool = False
    duckduckgo_url: str = (
        """https://server.smithery.ai/@nickclyde/duckduckgo-mcp-server/mcp?config={config_b64}&api_key={smithery_api_key}"""
    )
    duckduckgo_protocol: str = "streamable_http"
    duckduckgo_config: str = "b'e30='"

    # MCP Sequential Thinking Settings
    include_sequential_thinking: bool = False
    sequential_thinking_url: str = (
        """https://server.smithery.ai/@smithery-ai/server-sequential-thinking/mcp?config={config_b64}&api_key={smithery_api_key}"""
    )
    sequential_thinking_protocol: str = "streamable_http"
    sequential_thinking_config: str = "b'e30='"
