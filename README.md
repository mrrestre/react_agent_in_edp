https://medium.com/@adarsh.ajay/setting-up-postgresql-with-pgvector-in-docker-a-step-by-step-guide-d4203f6456bd

docker pull ankane/pgvector

docker run -e POSTGRES_USER=react_agent \
           -e POSTGRES_PASSWORD=react_agent \
           -e POSTGRES_DB=troubleshooting \
           --name react_agent \
           -p 5432:5432 \
           -d ankane/pgvector

psql -h localhost -U myuser -d mydatabase -p 5432

CREATE EXTENSION vector;

SELECT * FROM pg_extension;