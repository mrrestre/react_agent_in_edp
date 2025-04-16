"""Configuration parameters for agent, tools and proxies"""

import logging
from typing import Any, Dict, List, Tuple

from pydantic_settings import BaseSettings

# --------------- Agent Tools --------------- #


class SapHelpToolSettings(BaseSettings):
    """Settings for SAP Help Tool"""

    logger_name: str = "SAP Help Tool"
    name: str = "documentation_retriever"
    description: str = (
        "Receives a query of up to 5 words, searches through documentation, and returns a concise summary of the relevant content."
    )
    query_field_descr: str = (
        "A query composed of up to 5 words, each representing a technical object name. Words should be space-separated."
    )
    top_n_articles: int = 5
    max_article_size: int = 500 * 1024  # 500 KB
    summarization_prompt: str = """Given the user's query: "{query}"
Summarize the following markdown articles in no more than 200 words,
focusing on how they directly explain and provide context to the user's query.
Extract key information from the articles that helps to understand the query better.
Include all relevant technical information and technical objects in bullet points.
Markdown Articles:
---
{markdown_content}
---"""


class SourceCodeLookupSettings(BaseSettings):
    """Settings for Source Code Lookup"""

    logger_name: str = "Source Code Lookup Tool"
    name: str = "source_code_lookup"
    description: str = (
        "Returns a specific method or class implementation that matches the specified input parameter."
    )


class TroubleshootingSearchSettings(BaseSettings):
    """Settings for Troubleshooting Search"""

    logger_name: str = "Troubleshooting Search Tool"
    name: str = "troubleshooting_memories_retriever"
    description: str = """Searches long-term memory to retrieve eInvoicing domain-specific knowledge related to the query, 
including troubleshooting guides and details on Application, Invoice, and Message Level Responses using vector-based analysis."""
    query_field_descr: str = (
        "Query composed of one or more keywords related to the question. Separate keywords with spaces."
    )
    use_in_memory_store: bool = False


# --------------- Agent --------------- #


class AgentSettings(BaseSettings):
    """Settings for the Main Agent"""

    logger_name: str = "ReAct Agent"
    max_iterations: int = 10
    system_prompt: str = """
< Role >
You are an expert on Electronic Document Processing.
</ Role >

< Instructions >
Context: Peppol, UBL, eInvoicing.
{react_instructions}
Avoid bias based on physical appearance, ethnicity, or race.
Replace inappropriate language with inclusive language; politely refuse results, if that is not possible.
</ Instructions >

< Tools >
Refer always to the tools using memory as a first resort.
You have access to the following tools in order to resolve the incoming questions:
{tools}
</ Tools >

< Rules >
{rules}
</ Rules >"""
    rules: list[str] = [
        "Always use tools that relly in memory first, before looking for new information",
        "Do not call more than one tool at the same time",
        "Excecute the tools in synchron manner",
        "Always cross validate your outputs using different sources",
        "Before expressing the answer, ensure that the original question is answered",
    ]
    instructions: list[str] = [
        "1. Begin with an observation that outlines the primary task or question you want the agent to address.",
        "2. Analyze the observation to generate exactly one thought that leads to an actionable step using one of the available tools.",
        "3. Log the generated thought and corresponding action pair for transparency and future reference.",
        "4. Execute the exactly one action using the choosen tool and specify the parameters needed.",
        "5. Collect the new observation or insights generated from the tool's output.",
        """6. Is further analysis or action needed, think how other possible tools may help to improve the output?
        - If yes, create new thought and action pairs.
        - If no, provide a concise conclusion.""",
    ]
    # Output schema
    final_output_description: str = "The final output of the agent"
    reasoning_description: str = "The reasoning behind the final output"
    tools_used_description: str = "The tools used by the agent to achieve the result"


# --------------- MCP Servers --------------- #


class QAToolsServerSettings(BaseSettings):
    """Settings for QuestionAnsweringToolsServer"""

    name: str = "QuestionAnsweringTools"
    port: int = 8000
    host: str = "0.0.0.0"


class CodingsToolsServerSettings(BaseSettings):
    """Settings for CodingToolsServer"""

    name: str = "CodingTools"
    port: int = 8001
    host: str = "0.0.0.0"


# --------------- Utils --------------- #


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
    model: str = "gpt-4o"
    max_output_tokens: int = 1024
    temperature: float = 0.05
    max_input_tokens: int = 10000


class MemoryManagerSettings(BaseSettings):
    """Settings for the Memory Manager"""

    logger_name: str = "Memory Manager"
    embedding_model: str = "text-embedding-ada-002"
    dimensions: int = 1536
    postgres_conn_string: str = (
        "postgresql://react_agent:react_agent@localhost:5432/troubleshooting"
    )
    namespace: Tuple[str, str] = ("agent", "troubleshooting")
    memories_to_retrieve: int = 3


class TriageSettings(BaseSettings):
    """Settings for the Triage component"""

    logger_name: str = "Triage"
    sys_prompt: str = """
< Role >
You are in charge for the triage in an agent. Based on the question, you should decide the most fitting category for further processing
</ Role >

< Instructions >
In order to process the incomming question in the best manner, you should categorize the incoming question in exactly one of the following categories:
{categories}
</ Instructions >

< Rules >
{triage_rules}
</ Rules >

< Few shot examples >
{examples}
</ Few shot examples >"""
    instructions: List[Dict[str, str]] = [
        {
            "category": "Knowledge-QA",
            "description": "Question which an expert in the topic or a documentation/wiki/troubleshooting may respond",
        },
        {
            "category": "Config-RCA",
            "description": "Questions where Root Cause Analysis should be made in order to understand the issue",
        },
    ]
    examples: List[Dict[str, str]] = [
        {
            "question": "As a Public Cloud customer in Spain, can I extend an existing eDocument customer invoice Process?",
            "category": "Knowledge-QA",
        },
        {
            "question": "Explain how 'Payment Terms' is mapped. Start with 'map_invoice1'.",
            "category": "Config-RCA",
        },
        {
            "question": "I want to extend the standard E-Mail sent to customers, generate a sample code to enhance the E-Mail attachmentby adding additional file of type PDF.",
            "category": "Knowledge-QA",
        },
        {
            "question": "Explain how 'Payment Terms' is mapped. Start with 'map_invoice1'.",
            "category": "Config-RCA",
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
