"""Documentation retriever tool for the React agent."""

import base64
import os
from typing import Type
from langchain.tools.base import BaseTool
from openai import BaseModel
from pydantic import Field
import requests

from dotenv import load_dotenv

from react_agent.src.agent_tools.models.documentation_retriever_models import (
    ChatEntry,
    OauthTokenResponse,
    SearchRequestObject,
    SearchResponseObject,
)
from react_agent.src.config.system_parameters import DocumentationRetrieverSettings
from react_agent.src.util.logger import LoggerSingleton

_ = load_dotenv()
DEPLOYED_BASE_URL = os.getenv("DEPLOYED_BASE_URL")
IDP_SSO_URL = os.getenv("IDP_SSO_URL")
IDP_SSO_CLIENT_ID = os.getenv("IDP_SSO_CLIENT_ID")
IDP_SSO_CLIENT_SECRET = os.getenv("IDP_SSO_CLIENT_SECRET")

TOOL_SETTINGS = DocumentationRetrieverSettings()
LOGGER = LoggerSingleton.get_logger(TOOL_SETTINGS.logger_name)


class DocumentationRetrieverInputModel(BaseModel):
    """Input schema for documentation retriever"""

    url: str = Field(
        ...,
        query=TOOL_SETTINGS.query_field_descr,
    )


class DocumentationRetriever(BaseTool):
    """Tool for retrieving documentation from the remote service."""

    name: str = TOOL_SETTINGS.name
    description: str = TOOL_SETTINGS.description
    args_schema: Type[BaseModel] = DocumentationRetrieverInputModel

    def _run(self, query: str) -> str:

        chat_entry = ChatEntry(content=query)
        search_request_object = SearchRequestObject(chat_entries=[chat_entry])

        remote_url = f"{DEPLOYED_BASE_URL}{TOOL_SETTINGS.search_service_relative_path}"

        oauth_token_response = self.retrieve_oauth_token()

        headers = {
            "Authorization": f"Bearer {oauth_token_response.access_token}",
        }

        response = requests.post(
            remote_url,
            headers=headers,
            json=search_request_object.model_dump(),
            timeout=TOOL_SETTINGS.request_timeout,
        )

        assert (
            response.status_code == 200
        ), f"Error: {response.status_code} - {response.text}"

        json_object = SearchResponseObject.model_validate_json(response.text)
        return json_object.llm_response

    def retrieve_oauth_token(self) -> OauthTokenResponse:
        """retrieve oauth token from IDP SSO"""

        auth_string_raw: str = f"{IDP_SSO_CLIENT_ID}:{IDP_SSO_CLIENT_SECRET}"

        headers: dict[str, str] = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {base64.b64encode(auth_string_raw.encode()).decode()}",
        }
        response = requests.post(
            f"{IDP_SSO_URL}{TOOL_SETTINGS.oauth_token_path}",
            headers=headers,
            timeout=TOOL_SETTINGS.request_timeout,
        )

        assert (
            response.status_code == 200
        ), f"Failed to retrieve oauth token: {response.text}, status_code={response.status_code}"
        return OauthTokenResponse.model_validate_json(response.text)
