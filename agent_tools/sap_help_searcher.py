from typing import Type
import urllib.parse

import requests


from pydantic import BaseModel
from markdownify import markdownify as md

from agent_tools.i_agent_tool import IAgentTool
from util.llm_proxy import LLMProxy


class SearchInputModel(BaseModel):
    """Input schema for the search_sap_help tool."""

    query: str


class MockSapHelpSearcher(IAgentTool):
    """Mock tool for searching articles from SAP Help at help.sap.com."""

    name: str = "search_sap_help"
    description: str = "Search articles from SAP Help at help.sap.com"
    args_schema: Type[BaseModel] = SearchInputModel

    @staticmethod
    def method(query: str) -> str:
        """Mock method for searching articles from SAP Help at help.sap.com."""
        return f"Search SAP Help for '{query}'"


class SapHelpSearcher(IAgentTool):
    """Tool for searching articles from SAP Help at help.sap.com."""

    name: str = "search_sap_help"
    description: str = "Search articles from SAP Help at help.sap.com"
    args_schema: Type[BaseModel] = SearchInputModel

    @staticmethod
    def shorten_text(text, max_words=17000):
        """Shorten the text to a maximum number of words and add '...' at the end."""

        # Split the text into words
        words = text.split()

        # Check if the number of words is less than or equal to the maximum allowed words
        if len(words) <= max_words:
            return text

        # Shorten the text by joining the first max_words words and adding an ellipsis
        shortened_text = " ".join(words[:max_words]) + "..."

        return shortened_text

    @staticmethod
    def method(query: str) -> str:
        markdown = ""
        url = f"https://help.sap.com/http.svc/elasticsearch?area=content&version=&language=en-US&state=PRODUCTION&q={query}&transtype=standard,html,pdf,others&product=SAP_S4HANA_ON-PREMISE&to=19&advancedSearch=0&excludeNotSearchable=1"

        response = requests.get(url, timeout=10)

        # Ensure the request was successful
        response.raise_for_status()
        # Load the JSON response
        data = response.json()
        # Get the results
        results = data["data"]["results"]
        # Limit to the first 10 results
        results = results[:10]

        for result in results:
            # Get the URL
            url = result["url"]
            # Parse the URL
            parsed = urllib.parse.urlparse(url)
            # Split the path into segments
            segments = parsed.path.split("/")
            # Extract the desired segments
            product = segments[2]
            deliverable_loio = segments[3]
            topic_loio = segments[4]

            # Create new URL with the extracted data
            new_url = f"https://help.sap.com/http.svc/deliverableMetadata?deliverableInfo=1&toc=1&topic_url={topic_loio}&product_url={product}&deliverable_url={deliverable_loio}&version=LATEST&loadlandingpageontopicnotfound=true"
            # Make a GET request to the new URL
            new_response = requests.get(new_url, timeout=10)
            # Ensure the request was successful
            new_response.raise_for_status()
            # Load the JSON response
            deliverable_metadata = new_response.json()

            try:
                id_value = deliverable_metadata["data"]["deliverable"]["id"]
                build_no = deliverable_metadata["data"]["deliverable"]["buildNo"]
                file_path = deliverable_metadata["data"]["filePath"]
                url = f"https://help.sap.com/http.svc/pagecontent?deliverableInfo=1&deliverable_id={id_value}&file_path={file_path}&buildNo={build_no}"

                response = requests.get(url, timeout=10)
                response_data = response.json()
                markdown += "\n------\n" + md(
                    response_data.get("data", {}).get("body", {}),
                    escape_underscores=False,
                )
            except KeyError:
                continue

            llm_proxy = LLMProxy()
            markdown = llm_proxy.invoke(
                "Summarize and join sections that are similar to each other:\n"
                + SapHelpSearcher.shorten_text(text=str(markdown))
            )
        return markdown
