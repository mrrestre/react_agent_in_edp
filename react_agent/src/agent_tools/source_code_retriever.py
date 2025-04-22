"""Tool for searching source code in ABAP system"""

from typing import Type

from langchain.tools.base import BaseTool
from langchain_core.tools import ToolException

from pydantic import BaseModel, Field

from react_agent.src.config.system_parameters import SourceCodeRetrieverSettings
from react_agent.src.util.logger import LoggerSingleton
from react_agent.src.util.sap_system_proxy import SAPSystemProxy

TOOL_SETTINGS = SourceCodeRetrieverSettings()
LOGGER = LoggerSingleton.get_logger(TOOL_SETTINGS.logger_name)


class SourceCodeRetrieverInputModel(BaseModel):
    """Input schema for source_code_lookup"""

    class_name: str = Field(None, description=TOOL_SETTINGS.class_name_field_descr)


class SourceCodeRetriever(BaseTool):
    """Tool for searching source code in ABAP system"""

    name: str = TOOL_SETTINGS.name
    description: str = TOOL_SETTINGS.description
    args_schema: Type[BaseModel] = SourceCodeRetrieverInputModel

    def _run(self, class_name: str = None) -> str:
        """Use default source data for source code lookup"""
        LOGGER.info("Running source code lookup with class_name: %s", class_name)

        xco2_source_code = self._query_xco2_service(class_name=class_name)

        if xco2_source_code:
            return xco2_source_code
        else:
            # If no class_name or method_name is provided
            error = "Class not found in XCO2 service"

            LOGGER.error(error)
            raise ToolException(error)

    def _query_xco2_service(self, class_name: str) -> str:
        response = SAPSystemProxy().get_endpoint_https(f"classes('{class_name}')")
        return response.get("code")
