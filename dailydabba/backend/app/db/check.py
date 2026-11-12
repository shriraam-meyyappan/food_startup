"""Connectivity, UTC and migration readiness checks without exposing credentials."""

import json
from functools import lru_cache

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import BACKEND_ROOT, get_settings
from app.db.database import Database


class DatabaseNotReady(RuntimeError):
    """The database does not have the configuration/schema this code expects."""


@lru_cache
def expected_revision() -> str:
    revision = ScriptDirectory.from_config(
        Config(str(BACKEND_ROOT / "alembic.ini"))
    ).get_current_head()
    if revision is None:
        raise DatabaseNotReady("No migration head configured")
    return revision


def check_database(session: Session) -> dict[str, str]:
    session.execute(text("SELECT 1")).scalar_one()
    timezone = session.execute(text("SHOW TIME ZONE")).scalar_one()
    revisions = (
        session.execute(text("SELECT version_num FROM public.alembic_version"))
        .scalars()
        .all()
    )
    if timezone != "UTC" or revisions != [expected_revision()]:
        raise DatabaseNotReady(
            "Database configuration or migration revision is not current"
        )
    return {"status": "ready", "timezone": timezone, "revision": revisions[0]}


def main() -> None:
    settings = get_settings()
    if settings.database_url is None:
        raise SystemExit("Set DATABASE_URL in backend/.env first")
    database = Database.from_url(settings.database_url)
    try:
        with database.sessions() as session:
            print(json.dumps(check_database(session)))
    except (SQLAlchemyError, DatabaseNotReady):
        raise SystemExit(
            "Database not ready. Check PostgreSQL, credentials and migrations."
        ) from None
    finally:
        database.dispose()


if __name__ == "__main__":
    main()
