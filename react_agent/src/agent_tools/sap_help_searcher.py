"""Tool for searching articles from SAP Help at help.sap.com."""

from typing import Type
from urllib.parse import urlencode

import requests

from pydantic import BaseModel, Field, field_validator
from markdownify import markdownify as md

from langchain.tools.base import BaseTool
from langchain.prompts import PromptTemplate
from langchain_core.tools import ToolException

from react_agent.src.util.llm_proxy import LLM_PROXY
from react_agent.src.config.system_parameters import SapHelpToolSettings
from react_agent.src.util.logger import LoggerSingleton

TOOL_SETTINGS = SapHelpToolSettings()
LOGGER = LoggerSingleton.get_logger(TOOL_SETTINGS.logger_name)


class SapHelpInputModel(BaseModel):
    """Input schema for the search_sap_help tool."""

    query: str = Field(
        ...,
        description=TOOL_SETTINGS.query_field_descr,
    )

    @field_validator("query", mode="before")
    @classmethod
    def validate_query_word_count(cls, value):
        """Validation that input query does not have more than 5 words"""
        words = value.split()
        if len(words) > 5:
            raise ToolException("Query must contain at most 5 words.")
        return value


class SapHelpSearcher(BaseTool):
    """Tool for searching articles from SAP Help at help.sap.com."""

    name: str = TOOL_SETTINGS.name
    description: str = TOOL_SETTINGS.description
    args_schema: Type[BaseModel] = SapHelpInputModel

    def _run(self, query: str) -> str:
        """Method for searching articles from SAP Help at help.sap.com with a given query."""
        all_articles_markdown = ""

        if query == "" or not isinstance(query, str):
            LOGGER.error("Cannot perform search, whitout a valid query")
            raise ToolException("Cannot perform search, whitout a valid query")

        search_results = self.fetch_articles_with_query(query=query)

        if search_results:
            for result in search_results:
                # Only check articles where loio is present
                if result.get("loio") != "":
                    # Add article to markdown containing all article content
                    all_articles_markdown += self.fetch_article(
                        topic_loio=result.get("loio")
                    )
                else:
                    LOGGER.info(
                        "Skipping article with no LOIO: %s", result.get("title", "")
                    )
                    continue
        else:
            LOGGER.error("No articles found for query: %s", query)
            raise ToolException(
                "No articles found for query, try again with broader query."
            )

        return self.summarize_markdown(
            markdown_content=all_articles_markdown, query=query
        )

    def summarize_markdown(self, markdown_content: str, query: str) -> str:
        """Summarization method for articles found."""
        LOGGER.info("Summarizing markdown")

        # Create a PromptTemplate object
        prompt_template = PromptTemplate.from_template(
            TOOL_SETTINGS.summarization_prompt
        )

        # Format the prompt with your markdown content
        prompt = prompt_template.format(
            markdown_content=markdown_content,
            query=query,
            max_num_words=TOOL_SETTINGS.max_num_words,
        )

        # Try using the information from all articles, if it fails, try using the half of it
        try:
            return LLM_PROXY.invoke(input=prompt)
        except RuntimeError:
            LOGGER.warning("Markdown too long, trying again with half of it")
            words = prompt.split()
            prompt = "".join(words[: int(len(words) / 2)])
            return LLM_PROXY.invoke(input=prompt)

    def fetch_articles_with_query(self, query: str) -> list:
        """Return top n articles for query in sap.help"""
        LOGGER.info("Searching for articles with query: %s", query)

        search_query_params_dic = {
            "area": "content",
            "language": TOOL_SETTINGS.language,
            "state": TOOL_SETTINGS.article_state,
            "q": query,
            "transtype": "standard,html,pdf,others",
            "product": TOOL_SETTINGS.product_name,
            "to": TOOL_SETTINGS.top_n_articles,
        }

        search_query_str = urlencode(search_query_params_dic)
        search_url = f"https://help.sap.com/http.svc/elasticsearch?{search_query_str}"

        # Make a GET request to the new URL
        server_response = requests.get(search_url, timeout=10)

        # Ensure the request was successful
        try:
            server_response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            LOGGER.error("HTTP error occurred: %s", err)
            raise ToolException(
                f"Error occurred while fetching articles from SAP Help, error: {err}"
            ) from err

        # Load the JSON response
        response_json = server_response.json()

        # Get the first n results (Most relevant articles on top)
        search_results = response_json["data"]["results"]

        return search_results

    def fetch_article(self, topic_loio: str) -> str:
        """Fetch the content of an article for a given topic loio."""
        LOGGER.info("Fetching article with LOIO: %s", topic_loio)

        topic_query_params_dic = {
            "version": "LATEST",
            "language": TOOL_SETTINGS.language,
            "state": TOOL_SETTINGS.article_state,
            "product": TOOL_SETTINGS.product_name,
            "topic": topic_loio,
        }
        topic_query_str = urlencode(topic_query_params_dic)

        # Create new URL with the extracted data
        article_content_url = (
            f"https://help.sap.com/http.svc/getcontent?{topic_query_str}"
        )
        # Make a GET request to the new URL
        server_response = requests.get(article_content_url, timeout=10)

        # Ensure the request was successful
        try:
            server_response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            LOGGER.error("HTTP error occurred: %s", err)
            return ""

        # Load the JSON response
        response_json = server_response.json()

        # Check the size of the response content and if the content is contained
        response_content_size = len(server_response.content)

        if response_content_size < TOOL_SETTINGS.max_article_size and response_json[
            "data"
        ]["content"].get("content"):
            LOGGER.info(
                "Adding content of article with loio %s to markdown file",
                topic_loio,
            )
            # Transform content to markdown (from HTML)
            return md(
                response_json["data"]["content"]["content"],
                escape_underscores=False,
            )
        else:
            # If the article is bigger than a certain size or does not contain content, skip it
            LOGGER.info(
                "Skipping article with LOIO: %s, content size: %s bytes",
                topic_loio,
                response_content_size,
            )
            return ""
