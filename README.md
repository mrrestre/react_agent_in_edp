For setting a Postgres DB for the memory management follow:
https://medium.com/@adarsh.ajay/setting-up-postgresql-with-pgvector-in-docker-a-step-by-step-guide-d4203f6456bd

Steps:
1. Pull the docker image
docker pull ankane/pgvector

2. Create a docker container
docker run -e POSTGRES_USER=react_agent \
           -e POSTGRES_PASSWORD=react_agent \
           -e POSTGRES_DB=troubleshooting \
           --name react_agent \
           -p 5432:5432 \
           -d ankane/pgvector

3. Connect to container and enter the psql
psql -h localhost -U myuser -d mydatabase -p 5432

4. Create extension needed for storing vector
CREATE EXTENSION vector;

5. Run this command to test that it worked (If something is shown, then it worked)
SELECT * FROM pg_extension;