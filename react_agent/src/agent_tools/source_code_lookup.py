import os
from typing import Type, Optional

from langchain.tools.base import BaseTool
from langchain_core.tools import ToolException

from pydantic import BaseModel, Field, field_validator

from react_agent.src.util.abap_repository import ABAPClassRepository

TOOL_NAME = "source_code_lookup"
TOOL_DESCR = "Returns a specific method or class implementation that matches the specified input parameter."


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

    @field_validator("class_name", "method_name")
    @classmethod
    def check_either_or_both(cls, value, values):
        """Check that Either class_name or method_name (or both) is provided."""
        if values.get("class_name") is None and values.get("method_name") is None:
            raise ToolException(
                "Either class_name or method_name (or both) must be provided."
            )
        return value


class MockSourceCodeMethodLookup(BaseTool):
    name: str = TOOL_NAME
    description: str = TOOL_DESCR
    args_schema: Type[BaseModel] = LookupInputModel

    def _run(
        self, class_name: Optional[str] = None, method_name: Optional[str] = None
    ) -> str:
        """Use default source data for source code lookup"""
        code_repository = ABAPClassRepository()
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, "resources", "abap_source.txt")
            code_repository.index_source(file_path=file_path)

        except Exception as exc:
            raise ToolException(exc) from exc

        if class_name and method_name:
            try:
                return code_repository.get_content_by_class_and_method(
                    class_name=class_name, method_name=method_name
                )
            except KeyError as error:
                raise ToolException(error) from error

        if class_name:
            try:
                return code_repository.get_content_by_class(class_name=class_name)
            except KeyError as error:
                raise ToolException(error) from error

        if method_name:
            try:
                return code_repository.get_content_by_method(method_name=method_name)
            except KeyError as error:
                raise ToolException(error) from error

        raise ToolException(
            "Without class and or method name, not source code lookup possible"
        )
