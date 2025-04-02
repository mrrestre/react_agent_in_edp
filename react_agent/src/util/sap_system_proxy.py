import os
import requests
from dotenv import load_dotenv

_ = load_dotenv()

PATH_TO_CERT: str = "certificates/cacert.pem"
BACK_URL: str = os.getenv("SAP_BACKEND_URL")
SAP_CLIENT: str = os.getenv("SAP_CLIENT")
SAP_USER: str = os.getenv("SAP_USER")
SAP_PASSWORD: str = os.getenv("SAP_PASSWORD")


class SAPSystemProxy:
    """Simple proxy for sending request to SAP System"""

    @staticmethod
    def get_endpoint(endpoint: str) -> str:
        """Send a GET request to system with parameters defined in .env"""

        session = requests.Session()

        url = f"{BACK_URL}/{endpoint}?sap-client={SAP_CLIENT}"
        session.auth = (SAP_USER, SAP_PASSWORD)
        response = session.get(url=url, verify=os.path.abspath(PATH_TO_CERT))

        return response.text
