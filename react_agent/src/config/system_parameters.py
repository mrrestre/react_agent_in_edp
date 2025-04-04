"""Configuration parameters for agent, tools and proxies"""

# --------------- Agent Tools --------------- #

SAP_HELP_TOOL = {
    # General
    "NAME": "search_sap_help",
    "DESCRIPTION": """Returns documentation, including specific information on setup and
    configuration for eDocuments""",
    # Search parameters
    "TOP_N_ARTICLES": 5,
    "MAX_ARTICLE_SIZE": 500 * 1024,  # 500 KB
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
    "NAME": "search_troubleshooting_memories",
    "DESCRIPTION": """Returns eInvoicing domain specific knowledge related to the query string,
    such as troubleshooting information, or details on Application Responses, 
    Invoice Responses, Message Level Responses""",
    # Search parameters
    "USE_IN_MEMORY_STORE": False,
    "MEMORIES_LIMIT": 2,
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

MAIN_AGENT = {
    "MAX_ITERATIONS": 10,
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
    </ Tools >
    """,
}

# --------------- Proxies --------------- #

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
