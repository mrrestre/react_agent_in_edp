from typing import Literal

from pydantic import BaseModel, Field

from util.llm_proxy import LLMProxy

from config import router_config, agent_configs
from config.supported_llms import SupportedLLMs


class RouterModel(BaseModel):
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

    def route_input(self, initial_email) -> RouterModel:
        """Route the input email to the appropriate category
        based on its relevance and urgency."""

        system_prompt = router_config.ROUTER_SYSTEM_PROMPT.format(
            full_name=agent_configs.PROFILE["full_name"],
            name=agent_configs.PROFILE["name"],
            examples=None,
            user_profile_background=agent_configs.PROFILE["user_profile_background"],
            triage_no=agent_configs.PROMP_INSTRUCTIONS["triage_rules"]["ignore"],
            triage_notify=agent_configs.PROMP_INSTRUCTIONS["triage_rules"]["notify"],
            triage_email=agent_configs.PROMP_INSTRUCTIONS["triage_rules"]["respond"],
        )

        user_prompt = router_config.ROUTER_USER_PROMPT.format(
            author=initial_email["from"],
            to=initial_email["to"],
            subject=initial_email["subject"],
            email_thread=initial_email["body"],
        )

        llm_proxy = LLMProxy(model=SupportedLLMs.GPT_4o, max_tokens=10000)
        return llm_proxy.invoke_with_model(
            prompt=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            output_model=RouterModel,
        )
