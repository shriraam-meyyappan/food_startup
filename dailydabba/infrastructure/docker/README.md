# Local infrastructure

The root `docker-compose.yml` runs the official PostgreSQL 17 Alpine image.
No custom image is needed. PostgreSQL listens on localhost only and stores data
in the Compose-managed `postgres_data` volume.

Run Compose commands from the `dailydabba` directory. See the root README for
environment setup and commands. Changing credentials in `.env` does not change
an existing database volume; PostgreSQL uses these values on first initialization.
