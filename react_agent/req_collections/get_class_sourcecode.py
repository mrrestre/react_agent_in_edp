import os
import requests
from dotenv import load_dotenv

_ = load_dotenv()

backend_url: str = os.getenv("SAP_BACKEND_URL")
class_name = "ZPS_CL_EX_MB_MIGO_BADI"
url = f"{backend_url}classes?$filter=class_name eq '{class_name}'"
# url = f"{backend_url}classes({class_name})"

print(f"URL: {url}")

session = requests.Session()
session.auth = (os.getenv("SAP_USER"), os.getenv("SAP_PASSWORD"))

response = session.get(url=url)

print(f"output: {response.text}")
