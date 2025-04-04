from pydantic import BaseModel

import pytest

from langchain_core.tools import ToolException
from langchain.tools.base import BaseTool

from react_agent.src.agent_tools.sap_help_searcher import (
    SapHelpSearcher,
    TOOL_NAME,
    TOOL_DESCR,
    SAPHelpInputModel,
)
from react_agent.src.util.llm_proxy import LLMProxy


def test_tool_attributes():
    tool = SapHelpSearcher()
    assert tool.name == TOOL_NAME
    assert tool.description == TOOL_DESCR
    assert issubclass(tool.args_schema, BaseModel)
    assert isinstance(tool.args_schema, SAPHelpInputModel)

    assert issubclass(tool.__class__, BaseTool)


def test_no_query_shall_throw_exception():
    tool = SapHelpSearcher()
    with pytest.raises(ToolException):
        tool._run(query="")


def test_query_with_wrong_datatype_throw_exception():
    int_query: int = 42
    float_query: float = 42.42
    tupel_query: tuple = ("number", 42)

    tool = SapHelpSearcher()

    with pytest.raises(ToolException):
        tool._run(query=int_query)
    with pytest.raises(ToolException):
        tool._run(query=float_query)
    with pytest.raises(ToolException):
        tool._run(query=tupel_query)


def test_query_with_no_articles_shall_throw_exception():
    tool = SapHelpSearcher()
    with pytest.raises(ToolException):
        tool._run(query="abcdefghijklmnopqrstuvwxyz")


def test_non_empty_string_should_be_generated_from_query():
    tool = SapHelpSearcher()
    response = tool._run(query="unit testing")
    assert isinstance(response, str)
    assert response != ""


def test_llm_prxy_called_at_most_once():
    """Ensure the proxy is called at most once, proxy is a singleton"""
    llm_proxy = LLMProxy()
    tool = SapHelpSearcher()
    tool._run(query="unit testing")
    assert llm_proxy.call_count == 0 or llm_proxy.call_count == 1


def test_articles_fetch_with_query():
    query: str = "unit testing"
    top_n: int = 5
    tool = SapHelpSearcher()
    article_list = tool.fetch_articles_with_query(query=query, top_n=top_n)
    assert article_list
    assert isinstance(article_list, list)
    assert len(article_list) == top_n


def test_fetched_articles_sorted_by_score():
    query: str = "unit testing"
    top_n: int = 3
    tool = SapHelpSearcher()
    article_list = tool.fetch_articles_with_query(query=query, top_n=top_n)

    for i in range(len(article_list) - 1):
        current_score = float(article_list[i]["score"])
        next_score = float(article_list[i + 1]["score"])

        assert current_score > next_score


# TODO: Add test for ensure a certain level of queality in the summarization
