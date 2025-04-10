"""Configuration parameters for agent, tools and proxies"""

# --------------- Agent Tools --------------- #

SAP_HELP_TOOL = {
    # General
    "NAME": "documentation_retriever",
    "DESCRIPTION": "Receives a query of up to 5 words, searches through documentation, and returns a concise summary of the relevant content.",
    "QUERY_FIELD_DESCR": "A query composed of up to 5 words, each representing a technical object name. Words should be space-separated.",
    # Search parameters
    "TOP_N_ARTICLES": 5,
    "MAX_ARTICLE_SIZE": 500 * 1024,  # 500 KB
    # Prompt
    "SUMMARIZATION_PROMPT": """Given the user's query: "{query}"
Summarize the following markdown articles in no more than 200 words, 
focusing on how they directly explain and provide context to the user's query. 
Extract key information from the articles that helps to understand the query better.
Include all relevant technical information and technical objects in bullet points.
Markdown Articles:
---
{markdown_content}
---""",
}

SOURCE_CODE_LOOKUP = {
    # General
    "NAME": "source_code_lookup",
    "DESCRIPTION": "Returns a specific method or class implementation that matches the specified input parameter.",
}

TROUBLESHOOTING_SEARCH = {
    # General
    "NAME": "troubleshooting_memories_retriever",
    "DESCRIPTION": """Searches long-term memory to retrieve eInvoicing domain-specific knowledge related to the query, 
including troubleshooting guides and details on Application, Invoice, and Message Level Responses using vector-based analysis.""",
    "QUERY_FIELD_DESCR": "Query composed of one or more keywords related to the question. Separate keywords with spaces.",
    # Search parameters
    "USE_IN_MEMORY_STORE": False,
}

MASTER_DATA_GET = {
    # General
    "NAME": "get_master_data",
    "DESCRIPTION": """Returns master data and configuration that may be related to the source document. 
This information may be mapped directly or indirectly via Value Mappings into the XML, 
or control the way those values are mapped.""",
    "ENDPOINT": "/eDocument/master-data",
}

# --------------- Agent --------------- #

# TODO: Think adding additional instruction on the tool choosing
MAIN_AGENT = {
    # Configuration
    "MAX_ITERATIONS": 10,
    # Prompt
    "AGENT_SYSTEM_PROMPT": """
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
You have access to the following tools in order to resolve the incoming questions:
{tools}
Refer always to the tools using memory as a first resort.
</ Tools >

< Rules >
{rules}
</ Rules >""",
}

AGENT_RULES = [
    "Always use tools that relly in memory first, before looking for new information",
    "Do not call more than one tool at the same time",
    "Excecute the tools in synchron manner",
    "Cross validate the facts with different sources",
    "Before expressing the answer, ensure that the original question is answered",
]

REACT_INSTRUCTIONS = [
    "1. Begin with an observation that outlines the primary task or question you want the agent to address.",
    "2. Analyze the observation to generate exactly one thought that leads to an actionable step using one of the available tools.",
    "3. Log the generated thought and corresponding action pair for transparency and future reference.",
    "4. Execute the exactly one action using the choosen tool and specify the parameters needed.",
    "5. Collect the new observation or insights generated from the tool's output.",
    """6. Is further analysis or action needed, think how other possible tools may help to improve the output?
- If yes, create new thought and action pairs.
- If no, provide a concise conclusion.""",
]

# --------------- Utils --------------- #

LLM_PROXY = {
    "MODEL": "gpt-4o",
    "MAX_OUTPUT_TOKENS": 1024,
    "TEMPERATURE": 0.05,
    "MAX_INPUT_TOKENS": 10000,
}

MEMORY_MANAGER = {
    "EMBEDDING_MODEL": "text-embedding-ada-002",
    "DIMENSIONS": 1536,
    "POSTGRES_CONN_STRING": "postgresql://react_agent:react_agent@localhost:5432/troubleshooting",
    "NAMESPACE": ("agent", "troubleshooting"),
    "MEMORIES_TO_RETRIEVE": 3,
}

TRIAGE = {
    # Prompt
    "SYS_PROMPT": """
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
</ Few shot examples >""",
    "INSTRUCTIONS": [
        {
            "category": "Knowledge-QA",
            "description": "Question which an expert in the topic or a documentation/wiki/troubleshooting may respond",
        },
        {
            "category": "Config-RCA",
            "description": "Questions where Root Cause Analysis should be made in order to understand the issue",
        },
    ],
    "EXAMPLES": [
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
    ],
    "RESPONSE_SCHEMA": {
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
    },
}
