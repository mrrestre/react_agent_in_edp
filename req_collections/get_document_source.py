import os
import requests
from dotenv import load_dotenv

_ = load_dotenv()

remaining_string = "/eDocument/master-data"
backend_url: str = os.getenv("SAP_BACKEND_URL")
url = backend_url.rstrip("/") + "/" + remaining_string.lstrip("/")

# Check if the URL already has a query string
if "?" in url:
    url += "&sap-client=" + os.getenv("SAP_CLIENT")
else:
    url += "?sap-client=" + os.getenv("SAP_CLIENT")

print(f"URL: {url}")

session = requests.Session()
session.auth = (os.getenv("SAP_USER"), os.getenv("SAP_PASSWORD"))

response = session.get(url=url, verify=os.path.abspath("certificates/cacert.pem"))

print(f"output: {response.text}")
