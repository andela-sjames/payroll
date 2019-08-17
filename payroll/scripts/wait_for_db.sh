#!/usr/bin/env bash
set -e

function wait_db() {
python << END
import sys
import psycopg2
try:
  conn = psycopg2.connect(dbname="$POSTGRES_DB", user="$POSTGRES_USER", password="$POSTGRES_PASSWORD", host="$POSTGRESDB_HOST")
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}
until wait_db; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
>&2 echo "Postgres is up - continuing..."

scripts/start_server.sh
