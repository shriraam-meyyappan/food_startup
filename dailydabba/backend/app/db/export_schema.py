"""Render review-only PostgreSQL DDL without opening a database connection."""

import argparse
from pathlib import Path

from sqlalchemy import create_mock_engine

import app.models  # noqa: F401 -- register every mapping before exporting
from app.db.base import Base


def render_schema() -> str:
    """Compile PostgreSQL tables and indexes for review; never execute SQL."""
    statements: list[str] = [
        "-- Phase 3 design only. Not an Alembic migration.",
        "-- Generated from SQLAlchemy models. No database connection was used.",
        "-- ORM insert defaults (including UUIDs) are not SQL server defaults.",
    ]

    def collect(statement, *args, **kwargs) -> None:
        compiled = str(statement.compile(dialect=engine.dialect)).strip()
        statements.append("\n".join(line.rstrip() for line in compiled.splitlines()) + ";")

    engine = create_mock_engine("postgresql://", collect)
    Base.metadata.create_all(engine, checkfirst=False)
    return "\n\n".join(statements) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(render_schema(), encoding="utf-8")
    print(f"Wrote {len(Base.metadata.tables)} table definitions to {args.output}")


if __name__ == "__main__":
    main()
