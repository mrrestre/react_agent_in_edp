from langchain.tools.base import BaseTool

from src.util.sap_system_proxy import SAPSystemProxy

TOOL_NAME = "get_master_data"
TOOL_DESCR = "Returns master data and configuration that may be related to the source document. This information may be mapped directly or indirectly via Value Mappings into the XML, or control the way those values are mapped."
TOOL_ENDPOINT = "/eDocument/master-data"


class MockMasterDataGetter(BaseTool):
    name: str = TOOL_NAME
    description: str = TOOL_DESCR

    def _run(self) -> str:
        """Mock method returning the master data"""
        return "Mocked master data"


class MasterDataGetter(BaseTool):
    name: str = TOOL_NAME
    description: str = TOOL_DESCR

    def _run(self) -> str:
        """Fetch the master data from sap system"""
        fetched_master_data = SAPSystemProxy.get_endpoint(endpoint=TOOL_ENDPOINT)
        return f"Master data: {fetched_master_data}"
