# Setup
In order for the agent to run following steps should be fulfilled:
- Connection to Gen AI Core in a BTP subaccount for the comunication with an LLM
- Dependencies with poetry should be installed
- Environment variables should be set using a .env file (see bellow)
- If the local ABAP database want to be used, a docker container should be prepared and the wanted clases pre-indexed (see bellow)

## Connection with Gen AI Hub
(TODO: explain how to do this)

## Project dependencies
For intalling the dependencies of the project poetry is used and therefor should be installed. Python 3.13 is required.
After the installation of both poetry and python run this command

```bash
poetry install
```

This step installs all the required dependencies and creates a automatically creates a environment which could be used for running for the jupyter notebooks and the python scripts.

## Setting up environment variables
A file named ".env" should be created in the root folder and should contain following variables:

```
# Only needed if the triage agent is used
ORCHESTRATION_URL=<Gen AI Hub Orchestration Endpoint>

# Variables needed for connecting to SAP system containing the XCO2 API
SAP_BACKEND_HOSTNAME=er1-001.wdf.sap.corp
SAP_BACKEND_BASE_URL=https://er1-001.wdf.sap.corp/sap/opu/odata4/sap
SAP_BACKEND_XCO_PATH=zps_xco_rap_serv_v4/srvd_a2x/sap/zps_xco_rap_serv_def/0001
SAP_BACKEND_DB_PATH=zks_rap_serv_table/srvd_a2x/sap/zks_rap_serv_def/0001

# Variables for authentification in ER1 system
SAP_CLIENT=001
SAP_USER=<user>
SAP_PASSWORD=<password>

# Only needed if Smithery tool are to be consumed (can be created without costs)
SMITHERY_API_KEY=<key>

# Credentials for identity provider for consuming the DRC-Assitant endpoints
IDP_SSO_URL=<url>
IDP_SSO_CLIENT_ID=<client-id>
IDP_SSO_CLIENT_SECRET=<client-secret>

# Deployment url for the DRC-Assitant API
DEPLOYED_BASE_URL=<url>
```

## Creating a local database for storing vectors
For the management of memories a local postgres docker image is needed. This can be either made by hand, or by running a prepared script.

### Script
Run the script located here: 
- [Unix Script](./react_agent/src/scripts/setup_vector_db.sh) (only for unix based systems)
- [Windows Script](./react_agent/src/scripts/setup_vector_db.sh) (only for windows systems)

### Manual configuration of docker image

For setting a Postgres DB for the memory management follow:
https://medium.com/@adarsh.ajay/setting-up-postgresql-with-pgvector-in-docker-a-step-by-step-guide-d4203f6456bd

Steps:
1. Pull the docker image
```bash
docker pull ankane/pgvector
```

1. Create a docker container
```bash
docker run -e POSTGRES_USER=react_agent \
           -e POSTGRES_PASSWORD=react_agent \
           -e POSTGRES_DB=troubleshooting \
           --name react_agent \
           -p 5432:5432 \
           -d ankane/pgvector
```

1. Connect to container and enter the psql
```bash
psql -h localhost -U myuser -d mydatabase -p 5432
```

1. Create extension needed for storing vector
```bash
CREATE EXTENSION vector;
```

1. Run this command to test that it worked (If something is shown, then it worked)
```bash
SELECT * FROM pg_extension;
```

## Fill the local database with ABAP methods
For filling up the vector database with the methods from a list of classes the following two scripts has been prepared 
- [Using XCO2 Script](./react_agent/src/scripts/load_abap.code_xco2.py) - This reads a json file containg the names and description of a set of classes and fetches the code from each class from the XCO2 endpoint. The json file to be used can be set in the script directly. Here is an [Example](./react_agent/src/scripts/resources/class_subset.json) for a json file
- [Using Local Code Script](./react_agent/src/scripts/load_abap_code_local.py) - This indexes and summarizes ABAP code found in a local .txt file such as this [Example](./react_agent/src/scripts/resources/abap_source.txt) 
Caution: for running any of these scripts, a connection to Gen AI Hub musst be already stablished, since a step in the script is to create summaries of the code with an LLM for the vector search. If many classes are present in the json file, the excecution of the script may take long.

# Running the agent

For running the agent the jupyter notebook in [Link](./notebooks/agent_single_question.ipynb) can be used. Be aware that this contains the code for using MCP for the communication with the tools and the intergration of the triage agent. Both of this can be configured with the boolean variables at the begining of the notebook

By default, if no triage agent is used, all the developed tools are going to be provided to agent. If this should be changed, either a list containing the subset of tools can be prepared (See how this is done in the fabric class as an example [ToolFabric](./react_agent/src/util/tools_fabric.py) - lines 88-105).

The question to be asked should be assigned to the QUERY variable.
The DEBUG boolean adds debugging information such as system prompt and agent reasoning steps to the output.

# Additional components

## MCP
### Starting servers
```bash
poetry run python react_agent/src/mcp/code_server.py
poetry run python react_agent/src/mcp/qa_server.py
```

### Start MCP inspector
```bash
npx @modelcontextprotocol/inspector
```