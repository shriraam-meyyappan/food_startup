# Local infrastructure

The root `docker-compose.yml` runs the official PostgreSQL 17 Alpine image.
No custom image is needed. PostgreSQL listens on localhost only and stores data
in the Compose-managed `postgres_data` volume.

Run Compose commands from the `dailydabba` directory. See the root README for
environment setup and commands. Changing credentials in `.env` does not change
an existing database volume; PostgreSQL uses these values on first initialization.

Phase 4 adds fresh-volume role initialization in initdb/01_roles.sh. Bootstrap,
migration and application passwords are separate; set the safe root .env example
and matching backend URLs before starting Compose. The API must not use the
bootstrap account. Alembic grants runtime permissions during explicit migrations.
See ../../backend/docs/database-setup.md for the native setup verified on this
machine, Docker commands, existing-volume precautions and migration instructions.
Docker itself is not installed/tested here; native PostgreSQL 17.12 is running.
