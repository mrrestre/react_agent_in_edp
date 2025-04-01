from typing import Literal

from pydantic import BaseModel, Field

from llm_proxy import LLMProxy, SupportedLLMs

from src.config import system_configs

# Triage prompt
ROUTER_SYSTEM_PROMPT = """
< Role >
You are {full_name}'s executive assistant. You are a top-notch executive assistant who cares about {name} performing as well as possible.
</ Role >

< Background >
{user_profile_background}. 
</ Background >

< Instructions >

{name} gets lots of emails. Your job is to categorize each email into one of three categories:

1. IGNORE - Emails that are not worth responding to or tracking
2. NOTIFY - Important information that {name} should know about but doesn't require a response
3. RESPOND - Emails that need a direct response from {name}

Classify the below email into one of these categories.

</ Instructions >

< Rules >
Emails that are not worth responding to:
{triage_no}

There are also other things that {name} should know about, but don't require an email response. For these, you should notify {name} (using the `notify` response). Examples of this include:
{triage_notify}

Emails that are worth responding to:
{triage_email}
</ Rules >

< Few shot examples >
{examples}
</ Few shot examples >
"""

ROUTER_USER_PROMPT = """
Please determine how to handle the below email thread:

From: {author}
To: {to}
Subject: {subject}
{email_thread}"""


class RouterOutputModel(BaseModel):
    """Analyze the unread email and route it according to its content."""

    reasoning: str = Field(
        description="Step-by-step reasoning behind the classification."
    )
    classification: Literal["ignore", "respond", "notify"] = Field(
        description="The classification of an email: 'ignore' for irrelevant emails, "
        "'notify' for important information that doesn't need a response, "
        "'respond' for emails that need a reply",
    )


class Router:

    def __init__(
        self, model: SupportedLLMs = SupportedLLMs.GPT_4o, max_tokens: int = 1024
    ):
        self.llm_proxy = LLMProxy(model, max_tokens)

    def route_input(self, initial_email) -> RouterOutputModel:
        """Route the input email to the appropriate category
        based on its relevance and urgency."""

        system_prompt = ROUTER_SYSTEM_PROMPT.format(
            full_name=system_configs.PROFILE["full_name"],
            name=system_configs.PROFILE["name"],
            examples=None,
            user_profile_background=system_configs.PROFILE["user_profile_background"],
            triage_no=system_configs.TRIAGE_INSTRUCTIONS["triage_rules"]["ignore"],
            triage_notify=system_configs.TRIAGE_INSTRUCTIONS["triage_rules"]["notify"],
            triage_email=system_configs.TRIAGE_INSTRUCTIONS["triage_rules"]["respond"],
        )

        user_prompt = ROUTER_USER_PROMPT.format(
            author=initial_email["from"],
            to=initial_email["to"],
            subject=initial_email["subject"],
            email_thread=initial_email["body"],
        )

        return self.llm_proxy.invoke_with_output_model(
            output_model=RouterOutputModel,
            prompt=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
