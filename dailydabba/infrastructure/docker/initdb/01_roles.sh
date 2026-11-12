#!/bin/sh
set -eu
# Official PostgreSQL entrypoint runs this only on a new/empty volume.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
\getenv db POSTGRES_DB
\getenv migration_password MIGRATION_DB_PASSWORD
\getenv app_password APP_DB_PASSWORD
CREATE ROLE dailydabba_migrator LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD :'migration_password';
CREATE ROLE dailydabba_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD :'app_password';
ALTER DATABASE :"db" OWNER TO dailydabba_migrator;
REVOKE ALL ON DATABASE :"db" FROM PUBLIC;
GRANT CONNECT ON DATABASE :"db" TO dailydabba_app;
ALTER SCHEMA public OWNER TO dailydabba_migrator;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO dailydabba_app;
CREATE DATABASE dailydabba_test OWNER dailydabba_migrator;
REVOKE ALL ON DATABASE dailydabba_test FROM PUBLIC;
GRANT CONNECT ON DATABASE dailydabba_test TO dailydabba_app;
\connect dailydabba_test
ALTER SCHEMA public OWNER TO dailydabba_migrator;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO dailydabba_app;
SQL
