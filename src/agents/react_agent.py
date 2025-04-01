"""Description: ReAct Agent class to manage the React Agent and its tools."""

from langgraph.prebuilt import create_react_agent

from langchain.tools.base import BaseTool
from langchain.prompts import PromptTemplate

from src.config import system_configs

from src.util.llm_proxy import LLMProxy

AGENT_SYSTEM_PROMPT = """
< Role >
You are {full_name}'s executive assistant. You are a top-notch executive assistant who cares about {name} performing as well as possible. 
</ Role >

< Instructions >

{name} gets lots of emails. Your job is to categorize each email into one of three categories:

1. IGNORE - Emails that are not worth responding to or tracking
2. NOTIFY - Important information that {name} should know about but doesn't require a response
3. RESPOND - Emails that need a direct response from {name}

Classify the below email into one of these categories and then use your tools if the content of the email requires you to take action.

</ Instructions >

< Tools >
You have access to the following tools to help manage {name}'s communications and schedule:

1. write_email(to, subject, content) - Send emails to specified recipients
2. schedule_meeting(attendees, subject, duration_minutes, preferred_day) - Schedule calendar meetings
3. check_calendar_availability(day) - Check available time slots for a given day
</ Tools >

< Instructions >
{instructions}
</ Instructions >
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
        sys_prompt_template = PromptTemplate.from_template(AGENT_SYSTEM_PROMPT)

        return sys_prompt_template.format(
            full_name=system_configs.PROFILE["full_name"],
            name=system_configs.PROFILE["name"],
            instructions=system_configs.PROMP_INSTRUCTIONS["agent_instructions"],
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
