from pydantic import BaseModel

import pytest

from langchain_core.tools import ToolException
from langchain.tools.base import BaseTool

from react_agent.src.agent_tools.sap_help_searcher import SapHelpSearcher
from react_agent.src.util.llm_proxy import LLMProxy


def test_tool_attributes():
    tool = SapHelpSearcher()
    assert tool.name is not None
    assert tool.description is not None
    assert issubclass(tool.args_schema, BaseModel)

    assert issubclass(tool.__class__, BaseTool)


def test_no_query_shall_throw_exception():
    tool = SapHelpSearcher()
    with pytest.raises(ToolException):
        tool._run(query="")


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
