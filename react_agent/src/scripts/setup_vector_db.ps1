# Configuration variables
$POSTGRES_USER = "react_agent"
$POSTGRES_PASSWORD = "react_agent"
$POSTGRES_DB = "troubleshooting"
$POSTGRES_PORT = 5432
$DOCKER_IMAGE = "ankane/pgvector"
$CONTAINER_NAME = "react_agent"

Write-Host "Step 1: Pulling Docker image..."
docker pull $DOCKER_IMAGE

Write-Host "Step 2: Creating Docker container..."
docker run -e POSTGRES_USER=$POSTGRES_USER `
           -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD `
           -e POSTGRES_DB=$POSTGRES_DB `
           --name $CONTAINER_NAME `
           -p $POSTGRES_PORT `
           -d $DOCKER_IMAGE

Write-Host "Waiting for the database to be ready..."
Start-Sleep -Seconds 5

Write-Host "Step 3: Connecting to PostgreSQL and creating extension..."
docker exec -i $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE EXTENSION IF NOT EXISTS vector;"

Write-Host "Step 4: Verifying extension installation..."
docker exec -i $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT * FROM pg_extension;"

Write-Host "Done!"