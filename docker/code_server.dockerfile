# Use the Alpine-based Python 3.13.3 image
FROM python:3.13.3-alpine

# Set the working directory inside the container
WORKDIR /app

# --- Install System Dependencies using apk ---
# Update apk index and install necessary packages:
# curl: for downloading Poetry installer
# build-base: Alpine's equivalent of build-essential (for compiling packages)
# postgresql-dev: Provides libpq headers and libraries needed by psycopg
RUN apk update && \
    apk add --no-cache curl build-base postgresql-dev

# --- Install Poetry ---
# Set environment variables for Poetry installation and configuration
ENV POETRY_HOME="/opt/poetry"
# This tells Poetry to create the virtual environment inside the project directory (.venv)
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
# Add Poetry's bin directory to the PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Download and install Poetry using its official installer script
RUN curl -sSL https://install.python-poetry.org | python -

# --- Clean up System Build Dependencies ---
# Remove the build dependencies and package index cache to reduce image size
# We keep curl and postgresql-dev installed as they might be needed at runtime by psycopg
RUN apk del build-base && \
    rm -rf /var/cache/apk/*

# --- Copy Poetry Files ---
# Copy the Poetry configuration files first for better caching.
# Ensure these are in the same directory as your Dockerfile locally.
COPY pyproject.toml poetry.lock ./

# --- Dependency Management with Poetry ---
# Install dependencies using Poetry
RUN poetry install --only=coding_server --no-root

# --- Create Directories Needed at Runtime ---
# Create the logs directory that the application needs to write logs to
RUN mkdir -p /app/logs

# --- Copy Specific Application Files with Structure ---
# Copy only the necessary files, preserving their original directory structure
# relative to the project root.
RUN mkdir -p react_agent/src/mcp \
    react_agent/src/agent_tools \
    react_agent/src/config \
    react_agent/src/util \
    react_agent/src/scripts/resources

# Copy the individual files into their correct locations within /app
# Ensure these source paths match your local project structure relative to the Dockerfile
COPY react_agent/src/mcp/code_server.py ./react_agent/src/mcp/
COPY react_agent/src/agent_tools/source_code_retriever.py ./react_agent/src/agent_tools/
COPY react_agent/src/agent_tools/codebase_searcher.py ./react_agent/src/agent_tools/
COPY react_agent/src/config/system_parameters.py ./react_agent/src/config/
COPY react_agent/src/util/logger.py ./react_agent/src/util/
COPY react_agent/src/util/memory_manager.py ./react_agent/src/util/
COPY react_agent/src/util/sap_system_proxy.py ./react_agent/src/util/
COPY .env .

# --- Configure Python Path ---
# Set PYTHONPATH to include the current working directory (/app).
# This tells Python to look inside /app for packages, allowing it to find
# 'react_agent' and its submodules.
ENV PYTHONPATH=/app

# --- Container Configuration ---
# Expose the port that your code_server.py script listens on (assuming 8000)
EXPOSE 8000

# --- Command to Run the Application ---
# Define the command to run your application when the container starts
# 'poetry run' executes the command within the Poetry-managed virtual environment
# Run the script using its path relative to the WORKDIR (/app)
CMD ["poetry", "run", "python", "react_agent/src/mcp/code_server.py"]
