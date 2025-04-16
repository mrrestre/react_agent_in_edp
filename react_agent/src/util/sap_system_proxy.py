import json
import os
import http.client
import base64
from dotenv import load_dotenv

_ = load_dotenv()

BACKEND_HOSTNAME: str = os.getenv("SAP_BACKEND_HOSTNAME")

BACK_URL: str = os.getenv("SAP_BACKEND_URL")
SAP_CLIENT: str = os.getenv("SAP_CLIENT")
SAP_USER: str = os.getenv("SAP_USER")
SAP_PASSWORD: str = os.getenv("SAP_PASSWORD")


class SAPSystemProxy:
    """Simple proxy for sending request to SAP System"""

    @staticmethod
    def get_endpoint_https(endpoint: str) -> str:
        """Send a GET request to system with parameters defined in .env"""
        conn = http.client.HTTPSConnection(BACKEND_HOSTNAME)

        url = f"{BACK_URL}/{endpoint}?sap-client={SAP_CLIENT}"

        credentials = f"{SAP_USER}:{SAP_PASSWORD}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode(
            "utf-8"
        )

        headers = {
            "Content-type": "application/json",
            "Authorization": f"Basic {encoded_credentials}",
        }

        conn.request("GET", url=url, headers=headers)

        response = conn.getresponse()
        response_data = response.read()

        response_data = response_data.decode("utf-8")
        json_response = json.loads(response_data)

        return json_response
