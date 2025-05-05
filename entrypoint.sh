#!/bin/bash

# Wait for Postgres to be ready
echo "Waiting for RDSpostgres..."
# while ! echo > /dev/tcp/okyke.crwk2swcs1bq.eu-west-1.rds.amazonaws.com/5432 2>/dev/null; do
while ! echo > /dev/tcp/postgres/5432 2>/dev/null; do
  sleep 1
done

alembic upgrade head
python init_and_seed_db.py

exec uvicorn app.main:app --host 0.0.0.0 --port 8080
