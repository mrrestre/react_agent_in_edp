"""Configuration parameters for agent, tools and proxies"""

import logging
from typing import Any, Dict, List, Tuple

from pydantic_settings import BaseSettings

# --------------- Agent Tools --------------- #


class SapHelpToolSettings(BaseSettings):
    """Settings for SAP Help Tool"""

    logger_name: str = "SAP Help Tool"
    name: str = "get_doc_summary"
    description: str = (
        "Searches a knowledge database using a short query (max 5 words) and returns a concise summary of the relevant information found."
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


class TroubleshootingSearchSettings(BaseSettings):
    """Settings for Troubleshooting Search"""

    logger_name: str = "Troubleshooting Search Tool"

    # Tool Description
    name: str = "retrieve_troubleshooting_guide"
    description: str = (
        "Retrieves relevant troubleshooting guidance from a specialized knowledge base using semantic similarity to match the query."
    )

    # Input model description
    query_field_descr: str = (
        "Query composed of one or more keywords related to the question. Separate keywords with spaces."
    )

    # Tool specifics
    namespace: Tuple[str, str] = ("agent", "troubleshooting")


class SourceCodeRetrieverSettings(BaseSettings):
    """Settings for Source Code Retriever"""

    logger_name: str = "Source Code Retriever Tool"

    # Tool Description
    name: str = "source_code_retriever"
    description: str = "Returns source code for the classname of the input"

    # Input model description
    class_name_field_descr: str = "The name of the class to retrieve source code for"


class CodebaseSearcherSettings(BaseSettings):
    """Settings for Source Code Lookup"""

    logger_name: str = "Codebase Search Tool"

    # Tool Description
    name: str = "codebase_memories_searcher"
    description: str = (
        "Returns source code for methods that are related to the input query"
    )

    # Input model description
    query_field_descr: str = (
        "Query composed of one or more keywords related to the question. Separate keywords with spaces."
    )

    # Tool specifics
    namespace: Tuple[str, str] = ("agent", "source_code")


# --------------- Agent --------------- #


class AgentSettings(BaseSettings):
    """Settings for the Main Agent"""

    logger_name: str = "ReAct Agent"
    max_iterations: int = 10
    system_prompt: str = """
< Role >
You are an expert on Electronic Document Processing and SAP Document and Reporting Compliance.
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
        "1. Prioritize Memory First: Before using tools to search for or fetch new external information, always check if relevant information already exists in memory or internal knowledge tools. Use these memory tools first if applicable.",
        "2. Strict Sequential Execution: Execute only *one* tool action per reasoning cycle. Crucially, wait for the action to fully complete and return its result before proceeding to the next 'Thought' step. Do not initiate multiple tool calls concurrently.",
        "3. Cross-Validation Principle: Whenever feasible and necessary for accuracy (especially for factual claims or critical data), plan to cross-validate information obtained from one source by using a different, independent tool or source in a subsequent reasoning cycle.",
        "4. Avoid Redundant Calls: Do not call the exact same tool with the exact same parameters repeatedly unless there is a clear reason (e.g., retrying after a confirmed transient error). If exploring related information, formulate a new, distinct query or use different parameters.",
        "5. Completeness and Support Check: Before generating the 'Final Answer', explicitly review the original request and the gathered information. Ensure *all parts* of the request have been addressed and that the answer is well-supported by the findings recorded in the 'Observation (Result)' steps.",
        "6. Task Focus: Ensure every 'Thought' and planned 'Action' directly contributes to solving the original request or validating necessary information. Avoid unnecessary exploration or tool usage.",
        "7. Error Handling: If a tool call fails or returns an error, explicitly note this error in the 'Observation (Result)' step. Your next 'Thought' should address how to handle this error (e.g., retry the action, try different parameters, use an alternative tool, or acknowledge the inability to retrieve the specific information).",
    ]
    instructions: list[str] = [
        "1. Observation: Start by clearly stating the initial user request, task, or the current state of the problem you need to address.",
        "2. Thought: Analyze the Observation. Break down the task if complex. Identify what information is missing or what specific sub-task needs to be performed next. Formulate a clear reasoning chain: explain why a particular action is needed and how it will help address the Observation or move towards the final goal. Explicitly consider if information validation is required at this stage or after gathering initial data.",
        "3. Action Plan: Based on the Thought, explicitly state: a) The single specific tool you plan to use next. b) The precise input or parameters you will provide to that tool. This step clearly documents the one intended action before execution.",
        "4. Action: Execute the single tool call exactly as specified in the Action Plan. Name the exact tool to be used and the parameters to be provided. Call the choosen tool and await response.",
        "5. Observation (Result): WAIT until the tool executed in Step 4 completes and returns its output. Once the result is available, record the exact output or result received. Do not proceed without this result.",
        "6. Thought (Synthesis & Validation): Only after successfully receiving the Observation (Result) in Step 5, analyze it:",
        "    a. Synthesize: Does the result directly answer the part of the problem you were addressing? Integrate this new information with previous findings.",
        "    b. Quality Check & Validation Plan: Assess the reliability and completeness of the information. Is it ambiguous? Does it conflict with previous information? Crucially, decide if cross-validation or verification using another source/method is necessary. If yes, formulate a plan for this validation (this plan will lead to the next Thought/Action Plan cycle).",
        "    c. Next Step Decision: Determine if the overall task is complete. If yes, proceed to Final Answer. If no, identify the next logical question, information gap, or validation step based on your synthesis and validation assessment, and loop back to Step 2 (Thought) to plan the next sequential cycle.",
        "7. Final Answer: Once the iterative process determines the task is complete and information is sufficiently validated, construct the final response. Summarize the key findings derived from the sequential steps. For transparency, briefly mention the sources consulted or the validation steps taken, especially if conflicting information was encountered. Clearly state any remaining uncertainties or limitations.",
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
    prompt_template: str = """Provide a brief description (1 or 2 sentences) of what this ABAP method does, 
focusing on its main purpose and functionality, source code: 
{source_code}"""


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
