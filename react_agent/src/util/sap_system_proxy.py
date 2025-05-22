from enum import StrEnum
import json
import os
import http.client
import base64
from typing import Optional
from urllib.parse import urlencode
from dotenv import load_dotenv

_ = load_dotenv()

BACKEND_HOSTNAME: str = os.getenv("SAP_BACKEND_HOSTNAME")

BACKEND_BASE_URL: str = os.getenv("SAP_BACKEND_BASE_URL")
SAP_CLIENT: str = os.getenv("SAP_CLIENT")
SAP_USER: str = os.getenv("SAP_USER")
SAP_PASSWORD: str = os.getenv("SAP_PASSWORD")


class SAPSystemServices(StrEnum):
    """Enum for SAP System Services"""

    XCO2 = os.getenv("SAP_BACKEND_XCO_PATH")
    DB = os.getenv("SAP_BACKEND_DB_PATH")


class SAPSystemProxy:
    """Simple proxy for sending request to SAP System"""

    @staticmethod
    def get_endpoint_https(
        service_endpoint: SAPSystemServices,
        service_parameters: str,
        extra_query_parameters: Optional[dict] = None,
    ) -> str:
        """Send a GET request to system with parameters defined in .env"""
        conn = http.client.HTTPSConnection(BACKEND_HOSTNAME)

        query_parameters = {
            "sap-client": SAP_CLIENT,
        }

        # If extra query parameters are provided, merge them with the default ones
        if extra_query_parameters:
            query_parameters = {**(extra_query_parameters or {}), **query_parameters}

        query_str = urlencode(query_parameters)

        url = f"{BACKEND_BASE_URL}/{service_endpoint}/{service_parameters}?{query_str}"

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
