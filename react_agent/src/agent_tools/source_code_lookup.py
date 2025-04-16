"""Tool for searching source code in ABAP system"""

from typing import Type, Optional

from langchain.tools.base import BaseTool
from langchain_core.tools import ToolException

from pydantic import BaseModel, Field, field_validator

from react_agent.src.util.abap_repository import ABAPClassRepository
from react_agent.src.config.system_parameters import SourceCodeLookupSettings
from react_agent.src.util.logger import LoggerSingleton

TOOL_SETTINGS = SourceCodeLookupSettings()
LOGGER = LoggerSingleton.get_logger(TOOL_SETTINGS.logger_name)


class LookupInputModel(BaseModel):
    """Input schema for source_code_lookup"""

    class_name: Optional[str] = Field(
        None, description=TOOL_SETTINGS.class_name_field_descr
    )

    method_name: Optional[str] = Field(
        None,
        description=TOOL_SETTINGS.method_name_field_descr,
    )

    @field_validator("class_name", "method_name")
    @classmethod
    def check_either_or_both(cls, value, values):
        """Check that either class_name or method_name (or both) is provided."""
        if values.get("class_name") is None and values.get("method_name") is None:
            raise ToolException(
                "Either class_name or method_name (or both) must be provided."
            )
        return value


class SourceCodeLookup(BaseTool):
    """Tool for searching source code in ABAP system"""

    name: str = TOOL_SETTINGS.name
    description: str = TOOL_SETTINGS.description
    args_schema: Type[BaseModel] = LookupInputModel

    def _run(
        self, class_name: Optional[str] = None, method_name: Optional[str] = None
    ) -> str:
        """Use default source data for source code lookup"""
        LOGGER.info(
            "Running source code lookup with class_name: %s and method_name: %s",
            class_name,
            method_name,
        )
        code_repository = ABAPClassRepository(class_name=class_name)

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

        # If no class_name or method_name is provided
        error = "Without class and or method name, not source code lookup possible"

        LOGGER.error(error)
        raise ToolException(error)
