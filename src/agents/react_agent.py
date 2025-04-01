"""Description: ReAct Agent class to manage the React Agent and its tools."""

from langgraph.prebuilt import create_react_agent

from langchain.tools.base import BaseTool
from langchain.prompts import PromptTemplate

from src.config import system_configs

from src.util.llm_proxy import LLMProxy

AGENT_SYSTEM_PROMPT_QA = """
    < Role >
        You are an expert on Electronic Document Processing.
    </ Role >

    < Instructions >
        Context: Peppol, UBL, eInvoicing.
        Solve a question answering task with interleaving Thought, Action, Observation steps.
        {react_instructions}
        Avoid bias based on physical appearance, ethnicity, or race.
        Replace inappropriate language with inclusive language; politely refuse results, if that is not possible.
    </ Instructions >

    < Tools >
        You have access to the following tools in order to resolve the incoming questions:
        1. search_sap_help(query) - Returns documentation, including specific information on setup and configuration for eDocuments
    </ Tools >
"""


class ReActAgent:
    """ReAct Agent class to manage the React Agent and its tools."""

    def __init__(self, llm_proxy: LLMProxy, tool_list: list[BaseTool], max_iter: int):
        self.response = None

        self.tools = tool_list
        self.max_iter = max_iter

        self.agent = create_react_agent(
            model=llm_proxy.get_llm(), tools=self.tools, prompt=self.create_sys_prompt()
        )

    def create_sys_prompt(self) -> str:
        """Create the prompt for the agent based on AGENT_SYSTEM_PROMPT and the system config."""
        sys_prompt_template = PromptTemplate.from_template(AGENT_SYSTEM_PROMPT_QA)

        return sys_prompt_template.format(
            react_instructions=system_configs.REACT_INSTRUCTIONS["instructions"],
        )

    def get_agent_graph(self) -> str:
        """Get the agent's graph in Mermaid format."""
        return self.agent.get_graph().draw_mermaid_png()

    def run_and_print_agent_stream(self, user_message: str) -> None:
        """Evaluates user input and print the agent's stream of messages."""
        input_object = {"messages": [("user", user_message)]}

        config_object = {"recursion_limit": self.max_iter}

        for s in self.agent.stream(
            input=input_object, stream_mode="values", config=config_object
        ):
            message = s["messages"][-1]
            if isinstance(message, tuple):
                print(message)
            else:
                message.pretty_print()
