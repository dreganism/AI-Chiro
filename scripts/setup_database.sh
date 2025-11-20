#!/usr/bin/env bash
set -euo pipefail

DB_NAME=${DB_NAME:-sjwg_reporter}
DB_USER=${DB_USER:-sjwg_user}
DB_PASSWORD=${DB_PASSWORD:-change-me}

psql -v ON_ERROR_STOP=1 <<SQL
DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER')
   THEN
      CREATE ROLE $DB_USER LOGIN PASSWORD '$DB_PASSWORD';
   END IF;
END
$$;

CREATE DATABASE $DB_NAME OWNER $DB_USER;
SQL

echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME" >> .env
