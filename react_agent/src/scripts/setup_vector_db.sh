#!/bin/bash

# Configuration variables
POSTGRES_USER="react_agent"
POSTGRES_PASSWORD="react_agent"
POSTGRES_DB="troubleshooting"
POSTGRES_PORT=5432
DOCKER_IMAGE="ankane/pgvector"
CONTAINER_NAME="react_agent"

echo "Step 1: Pulling Docker image..."
docker pull $DOCKER_IMAGE

echo "Step 2: Creating Docker container..."
docker run -e POSTGRES_USER=$POSTGRES_USER \
           -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
           -e POSTGRES_DB=$POSTGRES_DB \
           --name $CONTAINER_NAME \
           -p $POSTGRES_PORT:5432 \
           -d $DOCKER_IMAGE

echo "Waiting for the database to be ready..."
sleep 5

echo "Step 3: Connecting to PostgreSQL and creating extension..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost \
                                   -U $POSTGRES_USER \
                                   -d $POSTGRES_DB \
                                   -p $POSTGRES_PORT \
                                   -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo "Step 4: Verifying extension installation..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost \
                                   -U $POSTGRES_USER \
                                   -d $POSTGRES_DB \
                                   -p $POSTGRES_PORT \
                                   -c "SELECT * FROM pg_extension;"

echo "Done!"
