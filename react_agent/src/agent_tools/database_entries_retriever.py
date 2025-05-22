"""Tool for searching source code in ABAP system"""

import json
from typing import Type

from langchain.tools.base import BaseTool
from langchain_core.tools import ToolException

from pydantic import BaseModel, Field

from react_agent.src.config.system_parameters import DBEntriesRetrieverSettings
from react_agent.src.util.logger import LoggerSingleton
from react_agent.src.util.sap_system_proxy import SAPSystemProxy, SAPSystemServices

TOOL_SETTINGS = DBEntriesRetrieverSettings()
LOGGER = LoggerSingleton.get_logger(TOOL_SETTINGS.logger_name)


class DatabaseEntriesRetrieverInputModel(BaseModel):
    """Input schema for tool <name>"""

    table_name: str = Field(None, description=TOOL_SETTINGS.class_name_field_descr)


class DBEntriesRetriever(BaseTool):
    """Tool for searching source code in ABAP system"""

    name: str = TOOL_SETTINGS.name
    description: str = TOOL_SETTINGS.description
    args_schema: Type[BaseModel] = DatabaseEntriesRetrieverInputModel

    def _run(self, table_name: str = None) -> str:

        LOGGER.info("Running source code lookup with class_name: %s", table_name)

        database_entries = self._query_db_service(table_name=table_name)

        if database_entries:
            return "\n".join(str(d) for d in database_entries)

    def _query_db_service(self, table_name: str) -> list[dict]:
        """Query the SAP database service for entries in a given table"""

        table_name = table_name.replace("/", "%2F")
        response = SAPSystemProxy.get_endpoint_https(
            service_endpoint=SAPSystemServices.DB,
            service_parameters=f"Table_Name/{table_name}",
        )

        if not response.get("table_entries"):
            error = f"No entries found in SAP database service for table {table_name}"
            LOGGER.error(error)
            raise ToolException(error)

        db_entries = json.loads(response.get("table_entries"))
        return db_entries[: TOOL_SETTINGS.max_entries]
