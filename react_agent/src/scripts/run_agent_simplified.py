"""This script runs a simplified ReAct agent with a set of predefined tools."""

from langchain.tools.base import BaseTool

from react_agent.src.agents.react_agent import ReActAgent

from react_agent.src.agent_tools.database_entries_retriever import DBEntriesRetriever
from react_agent.src.agent_tools.documentation_retriever import DocumentationRetriever
from react_agent.src.agent_tools.sap_help_searcher import SapHelpSearcher
from react_agent.src.agent_tools.troubleshooting_searcher import TroubleshootingSearcher
from react_agent.src.agent_tools.codebase_searcher import CodebaseSearcher
from react_agent.src.agent_tools.source_code_retriever import SourceCodeRetriever

DEBUG_MODE = True
QUERY = "question to be asked"

# Create the list of tools to be used
agent_tools: list[BaseTool]

# Available tools: DocumentationRetriever, TroubleshootingSearcher, SapHelpSearcher, CodebaseSearcher, SourceCodeRetriever, DBEntriesRetriever
agent_tools = [
    DocumentationRetriever(),
    SapHelpSearcher(),
    SourceCodeRetriever(),
    DBEntriesRetriever(),
]

agent = ReActAgent(tool_list=agent_tools)
if DEBUG_MODE:
    print(agent.get_system_prompt())

agent.run_agent_with_input(user_message=QUERY, debug=DEBUG_MODE)

run_data = agent.get_execution_data()

run_data.pretty_print()

print(run_data.final_output)
