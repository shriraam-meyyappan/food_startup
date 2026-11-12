"""Run frozen migrations with migration credentials, never application credentials."""

from alembic import context
from sqlalchemy import create_engine, pool

import app.models  # noqa: F401
from app.core.config import get_settings
from app.db.base import Base

settings = get_settings()
if settings.migration_database_url is None:
    raise RuntimeError(
        "Set MIGRATION_DATABASE_URL; runtime credentials cannot run migrations"
    )
url = settings.migration_database_url.get_secret_value()
target_metadata = Base.metadata

if context.is_offline_mode():
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(
        url,
        poolclass=pool.NullPool,
        hide_parameters=True,
        connect_args={"connect_timeout": 5, "options": "-c timezone=UTC"},
    )
    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()
