"""Guarded real-PostgreSQL fixtures and opt-in test configuration."""

import os
from unittest.mock import patch

import pytest
from alembic import command
from alembic.config import Config
from pydantic import SecretStr
from sqlalchemy import inspect, text
from sqlalchemy.engine import make_url

import app.models  # noqa: F401
from app.core.config import BACKEND_ROOT, get_settings
from app.db.base import Base
from app.db.database import Database


def pytest_addoption(parser):
    parser.addoption(
        "--run-db",
        action="store_true",
        help="Reset and test dailydabba_test (never development)",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "database: opt-in real PostgreSQL integration checks"
    )


@pytest.fixture(scope="session")
def databases(request):
    if not request.config.getoption("--run-db"):
        pytest.skip("Use --run-db with a dedicated TEST_DATABASE_URL")
    settings = get_settings()
    if not settings.test_database_url or not settings.database_url:
        pytest.fail("Configure TEST_DATABASE_URL and DATABASE_URL first")
    test_url = make_url(settings.test_database_url.get_secret_value())
    app_url = make_url(settings.database_url.get_secret_value())
    if test_url.database != "dailydabba_test" or test_url.database == app_url.database:
        pytest.fail(
            "Refusing to reset anything except the separate dailydabba_test database"
        )
    if (test_url.host, test_url.port) != (app_url.host, app_url.port):
        pytest.fail("Test and runtime credentials must refer to the same local server")
    engine = Database.from_url(settings.test_database_url)
    runtime_url = app_url.set(database=test_url.database)
    runtime = Database.from_url(
        SecretStr(runtime_url.render_as_string(hide_password=False))
    )
    config = Config(str(BACKEND_ROOT / "alembic.ini"))

    def migrate(action, target=None):
        with patch.dict(
            os.environ,
            {"MIGRATION_DATABASE_URL": settings.test_database_url.get_secret_value()},
        ):
            get_settings.cache_clear()
            try:
                if action == "check":
                    command.check(config)
                elif action == "upgrade":
                    command.upgrade(config, target)
                else:
                    command.downgrade(config, target)
            finally:
                get_settings.cache_clear()

    # Validate the actual target too, not only the URL's database component.
    with engine.engine.connect() as connection:
        actual_database = connection.execute(
            text("SELECT current_database()")
        ).scalar_one()
    if actual_database != "dailydabba_test":
        engine.dispose()
        runtime.dispose()
        pytest.fail(
            "Connected database is not dailydabba_test; refusing destructive reset"
        )
    existing = set(inspect(engine.engine).get_table_names(schema="public"))
    if existing - set(Base.metadata.tables) - {"alembic_version"}:
        engine.dispose()
        runtime.dispose()
        pytest.fail("Unknown tables in test database; refusing destructive reset")
    # Explicitly opted-in scratch DB only. Exercise both migration directions.
    migrate("downgrade", "base")
    migrate("upgrade", "head")
    migrate("downgrade", "base")
    assert set(inspect(engine.engine).get_table_names()) <= {"alembic_version"}
    migrate("upgrade", "head")
    try:
        yield engine, runtime, migrate
    finally:
        runtime.dispose()
        migrate("downgrade", "base")
        engine.dispose()
