import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

from agents.prompts.prompts import TRIAGE_SYSTEM_PROMPT, TRIAGE_USER_PROMPT
from agents.config.agent_configs import PROFILE, PROMP_INSTRUCTIONS
from models.router import Router


class ReActAgent:

    def __init__(self):
        self.user_prompt = None

        self.prepare_system_prompt()

        _ = load_dotenv()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro", google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        self.llm_router = self.llm.with_structured_output(Router)

    def prepare_system_prompt(self):
        self.system_prompt = TRIAGE_SYSTEM_PROMPT.format(
            full_name=PROFILE["full_name"],
            name=PROFILE["name"],
            examples=None,
            user_profile_background=PROFILE["user_profile_background"],
            triage_no=PROMP_INSTRUCTIONS["triage_rules"]["ignore"],
            triage_notify=PROMP_INSTRUCTIONS["triage_rules"]["notify"],
            triage_email=PROMP_INSTRUCTIONS["triage_rules"]["respond"],
        )

    def prepare_user_prompt(self, email):
        self.user_prompt = TRIAGE_USER_PROMPT.format(
            author=email["from"],
            to=email["to"],
            subject=email["subject"],
            email_thread=email["body"],
        )

    def run_agent(self, email):
        self.prepare_user_prompt(email)
        result = self.llm_router.invoke(
            [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_prompt},
            ]
        )

        print(result)
