"""Synchronous PostgreSQL engines and request-scoped sessions."""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from pydantic import SecretStr
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


@dataclass
class Database:
    engine: Engine
    sessions: sessionmaker[Session]

    @classmethod
    def from_url(cls, url: SecretStr) -> "Database":
        engine = create_engine(
            url.get_secret_value(),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=5,
            pool_timeout=10,
            hide_parameters=True,
            connect_args={"connect_timeout": 5, "options": "-c timezone=UTC"},
        )
        return cls(
            engine, sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
        )

    def dispose(self) -> None:
        self.engine.dispose()


def get_session(request: Request) -> Iterator[Session]:
    """Close/roll back unfinished work; a service must explicitly commit its unit of work."""
    database: Database | None = getattr(request.app.state, "database", None)
    if database is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Database unavailable")
    with database.sessions() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise


DbSession = Annotated[Session, Depends(get_session)]
