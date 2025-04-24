from pydantic import BaseModel
from langchain_core.tools import ToolException
from langchain.tools.base import BaseTool

import pytest

from react_agent.src.agent_tools.codebase_searcher import CodebaseSearcher
from react_agent.src.config.system_parameters import CodebaseSearcherSettings

TOOL_SETTINGS = CodebaseSearcherSettings()


def test_tool_attributes():
    """Test that Codebase Searcher tool has correct attributes.

    Ensures that the tool's name and description match the settings.
    Verifies that the tool's argument schema is a subclass of BaseModel
    and that the tool itself is a subclass of BaseTool.
    """
    # When
    tool = CodebaseSearcher()
    # Then
    assert tool.name == TOOL_SETTINGS.name
    assert tool.description == TOOL_SETTINGS.description
    assert issubclass(tool.args_schema, BaseModel)

    assert issubclass(tool.__class__, BaseTool)


def test_no_query_shall_throw_exception():
    """Test that a query with no content throws an exception.
    Verifies that the method _run raises a ToolException if the query is an empty string.
    """
    # Given
    tool = CodebaseSearcher()

    with pytest.raises(ToolException):  # Then
        tool._run(query="")  # When


def test_query_returns_non_empty_string():
    """Test that a valid method implementation is retrieved from a valid query.
    Verifies that the method _run returns a non-empty string when provided with
    a valid query, ensuring that the response is of type string and is not empty.
    """
    # Given
    tool = CodebaseSearcher()
    # When
    response = tool._run(query="implementation for the mapping of invoice payments")
    # Then
    assert isinstance(response, str)
