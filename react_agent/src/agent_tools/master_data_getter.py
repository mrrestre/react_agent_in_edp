from langchain.tools.base import BaseTool

from react_agent.src.util.sap_system_proxy import SAPSystemProxy

from react_agent.src.config.system_parameters import MASTER_DATA_GET


class MockMasterDataGetter(BaseTool):
    name: str = MASTER_DATA_GET.get("NAME")
    description: str = MASTER_DATA_GET.get("DESCRIPTION")

    def _run(self) -> str:
        """Mock method returning the master data"""
        return "Mocked master data"


class MasterDataGetter(BaseTool):
    name: str = MASTER_DATA_GET.get("NAME")
    description: str = MASTER_DATA_GET.get("DESCRIPTION")

    def _run(self) -> str:
        """Fetch the master data from sap system"""
        fetched_master_data = SAPSystemProxy.get_endpoint(
            endpoint=MASTER_DATA_GET.get("ENDPOINT")
        )
        return f"Master data: {fetched_master_data}"
