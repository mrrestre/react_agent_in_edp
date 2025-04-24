"""Configuration parameters for agent, tools and proxies"""

from enum import Enum
import logging
from typing import Any, Dict, List, Tuple

from pydantic_settings import BaseSettings

# --------------- Agent Tools --------------- #


class SapHelpToolSettings(BaseSettings):
    """Settings for SAP Help Tool"""

    logger_name: str = "SAP Help Tool"

    # Tool Description
    name: str = "get_doc_summary"
    description: str = (
        "Searches a knowledge database using a short query (max 5 words) and returns a concise summary of the relevant information found."
    )
    # Input model description
    query_field_descr: str = (
        "A query composed of up to 5 words, each representing a technical object name. Words should be space-separated."
    )
    # Tool specifics
    product_name: str = "SAP_S4HANA_ON-PREMISE"
    language: str = "en-US"
    article_state: str = "PRODUCTION"
    top_n_articles: int = 7
    max_article_size: int = 500 * 1024  # 500 KB
    summarization_prompt: str = """<Role>
You are an expert in in Electronic Document Processing, with deep domain knowledge in SAP Document and Reporting Compliance, Peppol, UBL, and eInvoicing standards.
</Role>

<Task>
Given the user's query: "{query}"
Summarize the following markdown content in no more than 500 words, focusing on how it explains and supports the user's query in the context of electronic document processing in S/4HANA.
Prioritize relevant technical details, including SAP-specific terminology, transaction codes, configuration steps, and technical objects (e.g., function modules, tables, BAPIs, SAP Notes).
Where appropriate, use bullet points to list key technical components or steps.
Avoid generalities; emphasize how the markdown content connects directly to the query.
If multiple articles are included, synthesize overlapping information.
```markdown
{markdown_content}
```
</Task>
"""


class TroubleshootingSearchSettings(BaseSettings):
    """Settings for Troubleshooting Search"""

    logger_name: str = "Troubleshooting Search Tool"

    # Tool Description
    name: str = "retrieve_troubleshooting_guide"
    description: str = (
        "Retrieves relevant knowledge from a specialized knowledge base using semantic similarity to match the query."
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
    name: str = "retrieve_source_code"
    description: str = (
        " Retrieves the complete source code for a given ABAP class. Use this only if a prior search for specific code snippets in memory was unsuccessful."
    )

    # Input model description
    class_name_field_descr: str = "The name of the ABAP class"


class CodebaseSearcherSettings(BaseSettings):
    """Settings for Source Code Lookup"""

    logger_name: str = "Codebase Search Tool"

    # Tool Description
    name: str = "search_codebase_memories"
    description: str = (
        "Your primary tool for finding relevant code snippets or specific methods within the codebase. It searches based on keywords. Prioritize using this tool first. If your initial search doesn't yield results, consider trying this tool again with different keywords or focusing on potential method names related to the query before resorting to fetching the full class source code."
    )

    # Input model description
    query_field_descr: str = (
        "A query consisting of one or more keywords related to the code you're looking for, separated by spaces."
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
You are an expert in Electronic Document Processing, with deep domain knowledge in SAP Document and Reporting Compliance, Peppol, UBL, and eInvoicing standards.
</ Role >

< Objective >
Use a reason-and-act (ReAct) approach to answer user questions with **clear, well-supported reasoning chains**, and **tool-validated outputs**. Final answers must reflect insights derived from specific tool calls or memory observations.
</ Objective >

< Instructions >
{react_instructions}
Always follow these behavioral standards:
- Avoid assumptions not supported by tool outputs or memory.
- Replace biased or inappropriate language with inclusive, respectful phrasing.
- If a respectful response cannot be generated, politely decline the request.
</ Instructions >

< Tools >
You have access to the following tools to gather facts, retrieve relevant data, and answer technical or compliance-related queries:
{tools}
Always prefer **Memory** or prior context tools before external sources.
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
        "1. Observation: Restate the user’s request or define the specific sub-task you are currently addressing. Clearly establish the focus of this reasoning cycle.",
        "2. Thought: Analyze the problem. Decide whether information is already available in memory or needs to be retrieved. Consider if this stage requires validation, synthesis, or a new data point.",
        "3. Action Plan: Formulate a high-level strategy outlining the sequence of major steps or phases you intend to take to successfully achieve the user's entire request.",
        "4. Action: Based on your current Observation, Thought, and the overall Action Plan, decide the specific immediate step to execute right now. If a tool should be used, name the selected tool with the parameters to be used. Do not take any further steps until a result is returned.",
        "5. Observation (Result): Record the exact output returned by the tool. Do not paraphrase or interpret—just state the result as received.",
        "6. Thought (Synthesis & Validation): Analyze the result in context:",
        "    a. Synthesize the new result with prior observations and tool outputs.",
        "    b. Check if the result is reliable, complete, and free from contradiction.",
        "    c. Decide whether validation is needed using another tool, or whether the result is sufficient to proceed.",
        "    d. Based on this, choose the next action or conclude the task.",
        "7. Final Answer: Once confident that all parts of the task have been addressed and validated, generate the final answer.",
        "    - Summarize key findings from the tool results.",
        "    - Clearly state how the tools were used to arrive at the answer.",
        "    - Mention any remaining uncertainties or limits if applicable.",
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
    prompt_template: str = """As an expert in ABAP development, provide a concise summary (1-2 sentences) of the primary purpose and key functionality of the following ABAP method.
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
You are a Triage Agent responsible for classifying user questions into the most appropriate category for downstream processing.
</ Role >

< Task >
Analyze the user question carefully and assign it to **exactly one** of the following categories:
{categories}
</ Task >

< Guidelines >
- Base your decision strictly on the nature of the question.
- Focus on **what kind of processing** the question requires (e.g., factual lookup vs. investigation).
- Always choose the **single most fitting** category, even if the question appears ambiguous.
</ Guidelines >

< Category Definitions >
{triage_rules}
</ Category Definitions >

< Examples >
Here are examples of how questions should be categorized:
{examples}
</ Examples >
"""

    class Categories(str, Enum):
        """Possible categories from the incomming query"""

        KNOWLEDGE_QA = "Knowledge-QA"
        CONFIG_RCA = "Config-RCA"

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
