"""Create fresh local databases/roles with an explicitly supplied admin URL.

This does not apply migrations and refuses to take over a database owned by
another role. Existing role passwords are never changed automatically.
"""

import argparse
import os

import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url

from app.core.config import get_settings


def provision(database_name: str) -> None:
    if database_name not in {"dailydabba", "dailydabba_test"}:
        raise ValueError(
            "Only the DailyDabba development/test databases may be provisioned"
        )
    settings = get_settings()
    if not settings.database_url or not settings.migration_database_url:
        raise ValueError("Set runtime and migration URLs first")
    app = make_url(settings.database_url.get_secret_value())
    migration = make_url(settings.migration_database_url.get_secret_value())
    admin = make_url(os.environ["BOOTSTRAP_DATABASE_URL"])
    if app.username != "dailydabba_app" or migration.username != "dailydabba_migrator":
        raise ValueError(
            "Local provisioning requires the documented application/migration role names"
        )
    if (app.host, app.port) != (migration.host, migration.port) or (
        app.host,
        app.port,
    ) != (admin.host, admin.port):
        raise ValueError("All provisioning connections must target the same server")
    kwargs = dict(
        host=admin.host,
        port=admin.port or 5432,
        dbname=admin.database,
        user=admin.username,
        password=admin.password,
        connect_timeout=5,
    )
    with psycopg.connect(**kwargs, autocommit=True) as connection:
        with connection.cursor() as cursor:
            for url in (migration, app):
                cursor.execute(
                    "SELECT rolsuper, rolcreatedb, rolcreaterole, rolreplication FROM pg_roles WHERE rolname = %s",
                    (url.username,),
                )
                flags = cursor.fetchone()
                if flags is not None and any(flags):
                    raise ValueError(
                        "Existing role has elevated privileges; refusing to reuse it"
                    )
                if flags is None:
                    cursor.execute(
                        sql.SQL(
                            "CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD {}"
                        ).format(
                            sql.Identifier(url.username), sql.Literal(url.password)
                        )
                    )
            cursor.execute(
                "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = %s",
                (database_name,),
            )
            owner = cursor.fetchone()
            if owner is None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {} OWNER {}").format(
                        sql.Identifier(database_name),
                        sql.Identifier(migration.username),
                    )
                )
            elif owner[0] != migration.username:
                raise ValueError("Refusing to change ownership of an existing database")
            cursor.execute(
                sql.SQL("REVOKE ALL ON DATABASE {} FROM PUBLIC").format(
                    sql.Identifier(database_name)
                )
            )
            cursor.execute(
                sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                    sql.Identifier(database_name), sql.Identifier(app.username)
                )
            )
    kwargs["dbname"] = database_name
    with psycopg.connect(**kwargs, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute("REVOKE ALL ON SCHEMA public FROM PUBLIC")
            cursor.execute(
                sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(
                    sql.Identifier(app.username)
                )
            )
    print(
        f"Provisioned {database_name}; passwords were not printed or changed for existing roles"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database", choices=["dailydabba", "dailydabba_test"], required=True
    )
    args = parser.parse_args()
    try:
        provision(args.database)
    except (psycopg.Error, ValueError, KeyError):
        raise SystemExit(
            "Provisioning failed. Check admin URL, existing ownership and role credentials."
        ) from None


if __name__ == "__main__":
    main()
