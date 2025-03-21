import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

from prompts.intial_prompts import TRIAGE_SYSTEM_PROMPT, TRIAGE_USER_PROMPT

from models.router import Router


# Example incoming email
email = {
    "from": "Alice Smith <alice.smith@company.com>",
    "to": "John Doe <john.doe@company.com>",
    "subject": "Quick question about API documentation",
    "body": """
Hi John,

I was reviewing the API documentation for the new authentication service and noticed a few endpoints seem to be missing from the specs. Could you help clarify if this was intentional or if we should update the docs?

Specifically, I'm looking at:
- /auth/refresh
- /auth/validate

Thanks!
Alice""",
}


class MainAgent:

    def __init__(self):
        _ = load_dotenv()

        self.api_key = os.getenv("GOOGLE_API_KEY")

        self.profile = {
            "name": "John",
            "full_name": "John Doe",
            "user_profile_background": "Senior software engineer leading a team of 5 developers",
        }

        self.prompt_instructions = {
            "triage_rules": {
                "ignore": "Marketing newsletters, spam emails, mass company announcements",
                "notify": "Team member out sick, build system notifications, project status updates",
                "respond": "Direct questions from team members, meeting requests, critical bug reports",
            },
            "agent_instructions": "Use these tools when appropriate to help manage John's tasks efficiently.",
        }

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro", google_api_key=self.api_key
        )

        self.llm_router = self.llm.with_structured_output(Router)

    def run_agent(self):
        system_prompt = TRIAGE_SYSTEM_PROMPT.format(
            full_name=self.profile["full_name"],
            name=self.profile["name"],
            examples=None,
            user_profile_background=self.profile["user_profile_background"],
            triage_no=self.prompt_instructions["triage_rules"]["ignore"],
            triage_notify=self.prompt_instructions["triage_rules"]["notify"],
            triage_email=self.prompt_instructions["triage_rules"]["respond"],
        )

        user_prompt = TRIAGE_USER_PROMPT.format(
            author=email["from"],
            to=email["to"],
            subject=email["subject"],
            email_thread=email["body"],
        )

        result = self.llm_router.invoke(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )

        print(result)
