"""Helper class for triaging the incoming question before configuring the agent"""

import os
import json

from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration.models.template import Template, TemplateValue
from gen_ai_hub.orchestration.models.response_format import ResponseFormatJsonSchema
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.service import OrchestrationService

from langchain.prompts import PromptTemplate

from dotenv import load_dotenv

from react_agent.src.config.system_parameters import TriageSettings, LlmProxySettings
from react_agent.src.util.logger import LoggerSingleton

TRIAGE_SETTINGS = TriageSettings()
LLM_PROXY_SETTINGS = LlmProxySettings()
LOGGER = LoggerSingleton.get_logger(TRIAGE_SETTINGS.logger_name)


class Triage:
    """Helper class for triaging the incoming question before configuring the agent"""

    def __init__(self):
        self.llm = LLM(
            name=LLM_PROXY_SETTINGS.model,
            version="latest",
            parameters={
                "max_tokens": LLM_PROXY_SETTINGS.max_output_tokens,
                "temperature": LLM_PROXY_SETTINGS.temperature,
            },
        )

        _ = load_dotenv()

    def triage_user_message(self, user_message: str) -> dict[str, str]:
        """Route the input question to the appropriate category
        based on its content."""
        LOGGER.info("Triaging user message: %s", user_message)

        orchestration_url = os.getenv("ORCHESTRATION_URL")

        template = self._prepare_template()

        config = OrchestrationConfig(template=template, llm=self.llm)

        orchestration_service = OrchestrationService(
            api_url=orchestration_url, config=config
        )

        result = orchestration_service.run(
            template_values=[TemplateValue(name="user_message", value=user_message)]
        )

        # Extract the response content
        response_object = json.loads(
            result.orchestration_result.choices[0].message.content
        )

        return {
            "user_query": response_object.get("properties").get("user_query"),
            "category": response_object.get("properties").get("category"),
        }

    def _prepare_template(self) -> Template:
        """Prepare the promp for the orchestration api call"""

        categories = "\n".join(category for category in TRIAGE_SETTINGS.Categories)

        triage_rules = "\n".join(
            f"Category: {instruction.get("category")}\tDescription: {instruction.get("description")}"
            for instruction in TRIAGE_SETTINGS.instructions
        )
        examples = "\n".join(
            f"Question: {example.get("question")}\tCategory{example.get("category")}"
            for example in TRIAGE_SETTINGS.examples
        )

        sys_prompt_template = PromptTemplate.from_template(TRIAGE_SETTINGS.sys_prompt)

        sys_message = sys_prompt_template.format(
            categories=categories, triage_rules=triage_rules, examples=examples
        )

        return Template(
            messages=[
                SystemMessage(sys_message),
                UserMessage("Here is the question: {{?user_message}}"),
            ],
            response_format=ResponseFormatJsonSchema(
                name="response",
                description="triage output",
                schema=TRIAGE_SETTINGS.response_schema,
            ),
        )
