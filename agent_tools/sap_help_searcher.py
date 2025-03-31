from typing import Type
from urllib.parse import urlencode

import requests

from pydantic import BaseModel, Field
from markdownify import markdownify as md

from langchain.tools.base import BaseTool
from langchain.prompts import PromptTemplate

from util.llm_proxy import LLMProxy

SUMMARIZATION_PROMPT = """
Given the user's query: "{query}"

Summarize the following markdown articles in no more than 200 words, focusing on how they directly explain and provide context to the user's query. Extract key information from the articles that helps to understand the query better.

Markdown Articles:
---
{markdown_content}
---

Query-Focused Summary:
"""


class SearchInputModel(BaseModel):
    """Input schema for the search_sap_help tool."""

    query: str = Field(..., description="Query to search articles within help.sap.com")


class MockSapHelpSearcher(BaseTool):
    """Mock tool for searching articles from SAP Help at help.sap.com."""

    name: str = "search_sap_help"
    description: str = (
        "Get a summary from knowledge articles with a given query from SAP Help at help.sap.com"
    )
    args_schema: Type[BaseModel] = SearchInputModel

    def _run(self, query: str) -> str:
        """Mock method for searching articles from SAP Help at help.sap.com."""
        return f"Search SAP Help for '{query}'"


class SapHelpSearcher(BaseTool):
    """Tool for searching articles from SAP Help at help.sap.com."""

    name: str = "search_sap_help"
    description: str = (
        "Get a summary from knowledge articles with a given query from SAP Help at help.sap.com"
    )
    args_schema: Type[BaseModel] = SearchInputModel

    def summarize_markdown(self, markdown_content: str, query: str) -> str:
        """Summarization method for articles found."""
        llm_proxy = LLMProxy()

        # Create a PromptTemplate object
        prompt_template = PromptTemplate.from_template(SUMMARIZATION_PROMPT)

        # Format the prompt with your markdown content
        prompt = prompt_template.format(markdown_content=markdown_content, query=query)

        return llm_proxy.invoke(prompt=prompt).content

    def fetch_articles_with_query(self, query: str, top_n: int) -> list:
        """Return top n articles for query in sap.help"""
        search_query_params_dic = {
            "area": "content",
            "language": "en-US",
            "state": "PRODUCTION",
            "q": query,
            "transtype": "standard,html,pdf,others",
            "product": "SAP_S4HANA_ON-PREMISE",
            "to": "19&advancedSearch=0",
            "excludeNotSearchable": "1",
        }
        search_query_str = urlencode(search_query_params_dic)
        search_url = f"https://help.sap.com/http.svc/elasticsearch?{search_query_str}"

        # Make a GET request to the new URL
        server_response = requests.get(search_url, timeout=10)
        # Ensure the request was successful
        server_response.raise_for_status()
        # Load the JSON response
        response_json = server_response.json()

        # Get the first n results (Most relevant articles on top)
        search_results = response_json["data"]["results"][:top_n]

        return search_results

    def fetch_article(self, topic_loio: str) -> str:
        """Fetch the content of an article for a given topic loio."""
        topic_query_params_dic = {
            "version": "LATEST",
            "language": "en-US",
            "state": "PRODUCTION",
            "product": "SAP_S4HANA_ON-PREMISE",
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
        server_response.raise_for_status()

        # Load the JSON response
        response_json = server_response.json()

        # Transform content to markdown (from HTML)
        return md(
            response_json["data"]["content"]["content"],
            escape_underscores=False,
        )

    def _run(self, query: str) -> str:
        """Method for searching articles from SAP Help at help.sap.com with a given query."""
        all_articles_markdown = ""

        search_results = self.fetch_articles_with_query(query=query, top_n=10)

        for result in search_results:
            # Add article to markdown containing all article content
            all_articles_markdown += self.fetch_article(topic_loio=result["loio"])

        return self.summarize_markdown(
            markdown_content=all_articles_markdown, query=query
        )
