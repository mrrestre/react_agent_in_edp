import os
from typing import Optional

from pydantic import BaseModel, Field, model_validator
from mcp.server.fastmcp import FastMCP
from langchain_core.tools import ToolException

from react_agent.src.util.abap_repository import ABAPClassRepository

mcp = FastMCP("SourceCodeLookup")


class LookupInputModel(BaseModel):
    """Input schema for source_code_lookup"""

    class_name: Optional[str] = Field(
        None,
        description="Name of the class without trailing or leading whitespaces",
    )

    method_name: Optional[str] = Field(
        None,
        description="Name of the method without trailing or leading whitespaces",
    )

    @model_validator(mode="before")
    @classmethod
    def check_either_class_or_method(cls, values):
        """Ensure either class_name or method_name (or both) is provided."""
        class_name = values.get("class_name")
        method_name = values.get("method_name")
        if class_name is None and method_name is None:
            raise ToolException(
                "Either 'class_name' or 'method_name' (or both) must be provided."
            )
        return values


@mcp.tool()
def source_code_lookup(input_model: LookupInputModel) -> str:
    """Returns a specific method or class implementation that matches the specified input parameter."""
    code_repository = ABAPClassRepository()
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "resources", "abap_source.txt")
        code_repository.index_source(file_path=file_path)

    except ToolException as exc:
        raise ToolException(exc) from exc

    if input_model.class_name and input_model.method_name:
        try:
            return code_repository.get_content_by_class_and_method(
                class_name=input_model.class_name, method_name=input_model.method_name
            )
        except KeyError as error:
            raise ToolException(error) from error

    if input_model.class_name:
        try:
            return code_repository.get_content_by_class(
                class_name=input_model.class_name
            )
        except KeyError as error:
            raise ToolException(error) from error

    if input_model.method_name:
        try:
            return code_repository.get_content_by_method(
                method_name=input_model.method_name
            )
        except KeyError as error:
            raise ToolException(error) from error

    raise ToolException(
        "Without class and or method name, not source code lookup possible"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
