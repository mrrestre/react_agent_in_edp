from pydantic import BaseModel

import pytest

from langchain_core.tools import ToolException
from langchain.tools.base import BaseTool

from react_agent.src.agent_tools.sap_help_searcher import SapHelpSearcher
from react_agent.src.config.system_parameters import SapHelpToolSettings
from react_agent.src.util.llm_proxy import LLMProxy

SETTINGS = SapHelpToolSettings()


def test_tool_attributes():
    """Test that SapHelpSearcher tool has correct attributes.

    Ensures that the tool's name and description match the settings.
    Verifies that the tool's argument schema is a subclass of BaseModel
    and that the tool itself is a subclass of BaseTool.
    """
    # When
    tool = SapHelpSearcher()
    # Then
    assert tool.name == SETTINGS.name
    assert tool.description == SETTINGS.description
    assert issubclass(tool.args_schema, BaseModel)

    assert issubclass(tool.__class__, BaseTool)


def test_no_query_shall_throw_exception():
    """Test that a query with no content throws an exception.
    Verifies that the method _run raises a ToolException if the query is an empty string.
    """
    # Given
    tool = SapHelpSearcher()

    with pytest.raises(ToolException):  # Then
        tool._run(query="")  # When


def test_query_with_wrong_datatype_throw_exception():
    """
    Test that a query with an incorrect data type throws an exception.
    Verifies that the method _run raises a ToolException if the query is not a string.
    """
    # Given
    int_query: int = 42
    float_query: float = 42.42
    tupel_query: tuple = ("number", 42)
    tool = SapHelpSearcher()

    with pytest.raises(ToolException):  # Then
        tool._run(query=int_query)  # When
    with pytest.raises(ToolException):  # Then
        tool._run(query=float_query)  # When
    with pytest.raises(ToolException):  # Then
        tool._run(query=tupel_query)  # When


def test_query_with_no_articles_shall_throw_exception():
    """
    Test that a query with no articles throws an exception.
    Verifies that the method _run raises a ToolException if the query does not return any articles.
    """
    # Given
    tool = SapHelpSearcher()

    with pytest.raises(ToolException):  # Then
        tool._run(query="abcdefghijklmnopqrstuvwxyz")  # When


def test_articles_fetch_with_query():
    """
    Test that the method fetch_articles_with_query returns a list of articles
    when given a valid query and a positive top_n.
    Verifies that the method returns a list of articles and that the length of
    the list is equal to top_n.
    """
    # Given
    query: str = "unit testing"
    top_n: int = 5
    tool = SapHelpSearcher()
    # When
    article_list = tool.fetch_articles_with_query(query=query, top_n=top_n)
    # Then
    assert article_list
    assert isinstance(article_list, list)
    assert len(article_list) == top_n


def test_fetched_articles_sorted_by_score():
    """
    Test that the method fetch_articles_with_query returns a list of articles
    sorted by their score when given a valid query and a positive top_n.
    Verifies that the method returns a sorted list of articles and that the
    score of each article is higher than the score of the next article in the
    list.
    """
    # Given
    query: str = "unit testing"
    top_n: int = 3
    tool = SapHelpSearcher()
    # When
    article_list = tool.fetch_articles_with_query(query=query, top_n=top_n)
    # Then
    for i in range(len(article_list) - 1):
        current_score = float(article_list[i]["score"])
        next_score = float(article_list[i + 1]["score"])

        assert current_score > next_score


def test_llm_proxy_called_exactly_once_by_summarization():
    """Ensure the proxy is called at most once, proxy is a singleton"""
    # Given
    llm_proxy = LLMProxy()
    llm_proxy.reset_call_count()
    tool = SapHelpSearcher()
    # When
    tool.summarize_markdown(
        markdown_content="this is a test for summarization of unit testing",
        query="unit testing",
    )
    # Then
    assert llm_proxy.call_count == 1


def test_non_empty_string_should_be_generated_from_query():
    """Test that a non-empty string is generated from a valid query.
    Verifies that the method _run returns a non-empty string when provided with
    a valid query, ensuring that the response is of type string and is not empty.
    """
    # Given
    tool = SapHelpSearcher()
    # When
    response = tool._run(query="unit testing")
    # Then
    assert isinstance(response, str)
    assert response != ""


# TODO: Add test for ensure a certain level of queality in the summarization
