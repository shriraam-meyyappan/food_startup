# DailyDabba backend — complete through Phase 5

**Detailed completed-work and remaining plan:** [implementation summary](docs/implementation-summary.md).
**Try Phase 5 now:** [authentication guide](docs/authentication.md).

The active FastAPI backend is running at <http://127.0.0.1:8000/docs> on this
machine. PostgreSQL 17.12 is running on 127.0.0.1:55432. Phase 4 was checked and
restored before Phase 5. All **80 tests pass** with one known upstream warning.
No frontend was modified. No address/order/subscription/payment API is implemented yet.

## What works now

- GET /api/v1/health: process liveness, `{"status":"ok"}`.
- GET /api/v1/ready: database/UTC/migration readiness, `{"status":"ready"}`.
- POST /api/v1/auth/register: creates a customer/profile/audit atomically.
- POST /api/v1/auth/login: Argon2 verification and short-lived signed access token.
- GET /api/v1/users/me: authenticated own-account/profile retrieval.
- PATCH /api/v1/users/me/profile: permitted own-profile fields only.
- GET /api/v1/admin/access-check: admin-only guard demonstration.
- GET /api/v1/kitchen/access-check: kitchen staff/admin guard demonstration.

There is no default admin password. Public requests cannot choose or change roles.
Trusted staff accounts use the password-prompt CLI described in the auth guide.
Roles and account status are read from the database on each protected request.

## Environment and software

Use Python 3.12+ (verified: 3.13.5), Git, and PostgreSQL 17. On this machine native
PostgreSQL is already installed, outside the repository and OneDrive. Docker is
not installed; Compose initialization is supplied but container launch is unverified.
The previous NestJS/Prisma starter in ../services/api is preserved historical work.
Both frontend apps remain blank starters and are outside the current scope.

The virtual environment and configured .env already exist here. Do not recreate
or overwrite them. For a fresh checkout:

```powershell
cd C:\Users\rmshr\OneDrive\Desktop\food_startup\dailydabba\backend
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Configure real local database URLs and generate a random JWT key BEFORE starting
that fresh setup; see the authentication and database guides. The example signing
key is intentionally rejected. Never commit .env or print passwords/tokens/keys.
Settings use absolute backend .env paths with OS environment variables taking
precedence. Real keys/passwords were generated into ignored local files, not docs.

requirements.in lists direct constraints; requirements.txt pins the tested full
environment. New Phase 5 dependencies are pwdlib[argon2], PyJWT and email-validator.
On Linux/macOS create the environment with python3 and use .venv/bin/python for
the commands below. Explicit interpreter paths avoid PowerShell activation-policy
changes and the Windows Store alias for bare python on this machine.

## Start, stop and verify

The API is already running now. After a reboot, start native PostgreSQL using the
[database guide](docs/database-setup.md), then run the API helper from backend:

```powershell
.\scripts\start-api.ps1
```

To stop only this managed API (leaving PostgreSQL running):

```powershell
.\scripts\stop-api.ps1
```

The helpers keep process identity and logs in ignored .local, never replace an
unrelated listener, and check process identity before stopping it. They do not
register a Windows service, enable public access or change execution policy.
The managed API does not auto-reload. For source editing, stop it and run an
interactive server instead:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --no-proxy-headers
```

Ctrl+C stops the interactive server. Do not start a second server on the same port.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/ready
.\.venv\Scripts\python.exe -m app.db.check
.\.venv\Scripts\python.exe -m alembic check
```

Expected: ok; ready; CLI ready/UTC/0001_initial; no new upgrade operations detected.
The database has 23 application tables plus alembic_version. Phase 5 added no schema
migration and did not change the applied initial revision. The application never
creates tables or runs migrations on startup. Services explicitly own commits;
request sessions close and roll back unfinished/failed work.

## Try authentication

Open [Swagger](http://127.0.0.1:8000/docs). Register with your own email/name and a
private 12–128-character password; expect 201 and role customer. Login with the
same credentials; expect a bearer access token. Paste only the token value into
Swagger's Authorize field. GET /users/me and PATCH /users/me/profile should work;
admin/kitchen checks should return 403 for a customer. This denial is intentional.

The [authentication guide](docs/authentication.md) provides complete field contracts,
expected errors, a password-prompt PowerShell example, privileged account creation,
rate-limit behavior, token lifetime, safeguards and current production limitations.
It contains no real password, signing key or token.

## Run tests

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -q --run-db
```

Expected: no broken requirements; ordinary run **41 passed, 39 skipped**; full
opt-in run **80 passed**. One known Starlette/AnyIO deprecated-alias warning remains.
Password hashing and real database checks mean the full suite can take a minute
or more. Tests do not contact a payment or notification provider.

--run-db intentionally resets only the disposable dailydabba_test database. The
fixture verifies the ACTUAL connected database name, rejects development or unknown
tables, tests upgrade/downgrade, and cleans up afterward. Do not keep useful data
there. Authentication requests use real runtime-role sessions, not elevated
migration sessions. Failed-registration rollback and concurrent duplicate signup
are tested against PostgreSQL.

## Documentation and responsibilities

- [Implementation summary/remaining plan](docs/implementation-summary.md): detailed history through Phase 5 and Phases 6–15 plan.
- [Architecture](docs/architecture.md): routes/schemas/services/repositories/models and request flow.
- [Database design](docs/database-design.md): 23 tables, Mermaid ER diagram, all columns and constraints.
- [Database setup](docs/database-setup.md): native/Docker setup, credentials, session permissions and safe migrations.
- [Authentication](docs/authentication.md): real API walkthrough, staff accounts and security boundaries.
- [Progress](PROGRESS.md): compact continuation handoff and next confirmation point.
- [Review-only schema](docs/schema.sql) and [SQL examples](docs/example_queries.sql): design/reference artifacts; Alembic is authoritative for schema changes.

The code is a modular monolith. main.py builds the app/lifecycle. Routes handle
HTTP, schemas validate contracts, services coordinate transactions, repositories
issue queries, and models define storage. Security helpers do hashing/JWT verification;
request dependencies check current users/roles. No generic microservice framework
or frontend component was introduced.

Phase 5 is complete and awaits confirmation. Next is Phase 6: own-address management.
No Phase 6 feature is implemented yet. Source changes remain uncommitted for review;
Git identity, initial commit and frontend apps are unchanged.

## Complete current source and configuration

Backend paths below are relative to:
C:/Users/rmshr/OneDrive/Desktop/food_startup/dailydabba/backend.
Real local environment/admin secrets, binary installations, database data and caches
are excluded. Complete safe source/configuration code follows; documentation/SQL
artifacts are linked above. Every source file is also available directly in app/,
alembic/ and scripts/ for normal editing.

### .gitignore

```text
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
htmlcov/
.env
.env.*
!.env.example
*.log

.local/
```

### .env.example

```text
APP_NAME=DailyDabba API
LOG_LEVEL=INFO
# Runtime credentials: no schema ownership or migration privileges.
DATABASE_URL="postgresql+psycopg://dailydabba_app:replace_app_password@127.0.0.1:5432/dailydabba"
# Migration credentials: never use these for the running FastAPI application.
MIGRATION_DATABASE_URL="postgresql+psycopg://dailydabba_migrator:replace_migration_password@127.0.0.1:5432/dailydabba"
# Optional: dedicated empty test database, never your development database.
# TEST_DATABASE_URL="postgresql+psycopg://dailydabba_migrator:replace_migration_password@127.0.0.1:5432/dailydabba_test"

# Generate a fresh secret; never use the placeholder or print the real key.
JWT_SECRET=replace_with_a_random_secret_before_starting
JWT_ISSUER=dailydabba-api
JWT_AUDIENCE=dailydabba-clients
ACCESS_TOKEN_MINUTES=15
AUTH_RATE_LIMIT_PER_MINUTE=10
```

### requirements.in

```text
# Direct backend dependencies through Phase 5. requirements.txt pins the tested full resolution.
fastapi>=0.115,<1
uvicorn>=0.30,<1
pydantic>=2.10,<3
pydantic-settings>=2.6,<3
pytest>=8,<10
httpx>=0.27,<1

# Keep the HTTPX-based TestClient on Starlette's compatible pre-1.0 line.
starlette>=0.46,<1

# SQLAlchemy 2.0 models, PostgreSQL driver and migrations.
SQLAlchemy>=2.0,<2.1

alembic>=1.16,<2
psycopg[binary]>=3.2,<4

# Password hashing, signed JWTs and Pydantic email validation.
pwdlib[argon2]>=0.2,<1
PyJWT>=2.10,<3
email-validator>=2.2,<3
```

### requirements.txt

```text
alembic==1.20.1
annotated-doc==0.0.6
annotated-types==0.8.0
anyio==4.16.0
argon2-cffi==25.1.0
argon2-cffi-bindings==26.2.0
certifi==2026.10.23
cffi==2.1.1
click==8.5.1
colorama==0.4.6
dnspython==2.9.2
email-validator==2.3.0
fastapi==0.162.5
greenlet==3.5.6
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.20
iniconfig==2.3.1
Mako==1.4.3
MarkupSafe==3.0.4
opentelemetry-api==1.45.2
packaging==26.3
pluggy==1.7.0
psycopg==3.3.9
psycopg-binary==3.3.9
pwdlib==0.3.1
pycparser==3.12
pydantic==2.14.3
pydantic-settings==2.16.2
pydantic_core==2.50.4
Pygments==2.21.0
PyJWT==2.15.1
pytest==9.2.0
python-dotenv==1.2.4
SQLAlchemy==2.0.57
starlette==0.52.1
typing-inspection==0.4.5
typing_extensions==4.16.0
tzdata==2026.6
uvicorn==0.54.0
```

### pytest.ini

```text
[pytest]
testpaths = app/tests
pythonpath = .
```

### alembic.ini

```text
[alembic]
script_location = %(here)s/alembic
prepend_sys_path = %(here)s
path_separator = os
# URLs come from environment settings, never from this tracked file.
```

### alembic/script.py.mako

```text
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
"""

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

### app/__init__.py

```python
"""DailyDabba backend application."""
```

### app/api/__init__.py

```python
"""HTTP API routes."""
```

### app/api/dependencies.py

```python
"""Verified bearer identities and live database-backed role authorization."""

from typing import Annotated, Callable
from uuid import UUID

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings
from app.core.security import decode_access_token
from app.db.database import DbSession
from app.models.identity import User
from app.repositories import users

bearer = HTTPBearer(auto_error=False)


def request_settings(request: Request) -> Settings:
    return request.app.state.settings


RequestSettings = Annotated[Settings, Depends(request_settings)]


def unauthenticated() -> HTTPException:
    return HTTPException(
        401, "Invalid or expired credentials", headers={"WWW-Authenticate": "Bearer"}
    )


def token_subject(
    settings: RequestSettings,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> UUID:
    if credentials is None:
        raise unauthenticated()
    return decode_access_token(credentials.credentials, settings)


def current_user(
    subject: Annotated[UUID, Depends(token_subject)], session: DbSession
) -> User:
    user = users.by_id(session, subject)
    if user is None or not user.is_active or user.deactivated_at is not None:
        raise unauthenticated()
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def require_roles(*roles: str) -> Callable:
    def authorize(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(403, "Insufficient permissions")
        return user

    return authorize


def throttle_auth(request: Request) -> None:
    host = request.client.host if request.client else "unknown"
    retry = request.app.state.auth_limiter.retry_after(host + ":" + request.url.path)
    if retry is not None:
        raise HTTPException(
            429, "Too many authentication requests", headers={"Retry-After": str(retry)}
        )
```

### app/api/v1/__init__.py

```python
"""Version 1 API routes."""
```

### app/api/v1/access.py

```python
"""Role-guard demonstrations only; operational APIs remain Phase 12 work."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import require_roles
from app.models.identity import User
from app.schemas.auth import AccessResponse

router = APIRouter(tags=["Role access checks"])


@router.get("/admin/access-check", response_model=AccessResponse)
def admin_access(
    user: Annotated[User, Depends(require_roles("admin"))],
) -> AccessResponse:
    return AccessResponse(role=user.role)


@router.get("/kitchen/access-check", response_model=AccessResponse)
def kitchen_access(
    user: Annotated[User, Depends(require_roles("admin", "kitchen_staff"))],
) -> AccessResponse:
    return AccessResponse(role=user.role)
```

### app/api/v1/auth.py

```python
"""Frontend-independent JSON registration and password login endpoints."""

from fastapi import APIRouter, Depends

from app.api.dependencies import RequestSettings, throttle_auth
from app.core.security import require_signing_key
from app.db.database import DbSession
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services import auth

router = APIRouter(
    prefix="/auth", tags=["Authentication"], dependencies=[Depends(throttle_auth)]
)


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, session: DbSession) -> UserResponse:
    return auth.register(session, payload)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest, settings: RequestSettings, session: DbSession
) -> TokenResponse:
    require_signing_key(settings)
    return auth.login(
        session, str(payload.email), payload.password.get_secret_value(), settings
    )
```

### app/api/v1/health.py

```python
"""Process health endpoint; database readiness is a later phase."""

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return HTTP 200 when this application can serve requests."""
    return HealthResponse(status="ok")
```

### app/api/v1/readiness.py

```python
"""Database readiness is separate from process liveness."""

import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.db.check import DatabaseNotReady, check_database
from app.db.database import DbSession
from app.schemas.health import ReadinessResponse

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)


@router.get("/ready", response_model=ReadinessResponse)
def readiness(session: DbSession) -> ReadinessResponse:
    """Require a reachable, UTC-configured database at the current migration head."""
    try:
        check_database(session)
    except (SQLAlchemyError, DatabaseNotReady):
        logger.warning("Database readiness check failed")
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    return ReadinessResponse(status="ready")
```

### app/api/v1/router.py

```python
"""Assemble the version 1 API independently of the application entry point."""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.readiness import router as readiness_router
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.access import router as access_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)

api_router.include_router(readiness_router)

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(access_router)
```

### app/api/v1/users.py

```python
"""Self-service profile access, never arbitrary user-ID updates."""

from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.db.database import DbSession
from app.schemas.auth import ProfileUpdate, UserResponse
from app.services.profiles import update_profile

router = APIRouter(prefix="/users", tags=["Current user"])


@router.get("/me", response_model=UserResponse)
def me(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user)


@router.patch("/me/profile", response_model=UserResponse)
def patch_profile(
    payload: ProfileUpdate, user: CurrentUser, session: DbSession
) -> UserResponse:
    return update_profile(session, user, payload)
```

### app/cli/__init__.py

```python
"""Explicit local administration commands, never public API endpoints."""
```

### app/cli/create_staff.py

```python
"""Create an admin or kitchen account via a trusted local password prompt."""

import argparse
from getpass import getpass

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.db.database import Database
from app.schemas.auth import RegisterRequest
from app.services.auth import AccountExists, create_account


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    parser.add_argument("--full-name", required=True)
    parser.add_argument("--role", choices=["admin", "kitchen_staff"], required=True)
    args = parser.parse_args()
    settings = get_settings()
    if settings.migration_database_url is None:
        raise SystemExit("This trusted local command requires migration credentials")
    password = getpass("Password (12–128 characters): ")
    if password != getpass("Confirm password: "):
        raise SystemExit("Passwords do not match")
    try:
        payload = RegisterRequest(
            email=args.email, full_name=args.full_name, password=password
        )
    except ValidationError:
        raise SystemExit(
            "Invalid email, name or password; see the authentication guide"
        ) from None
    database = Database.from_url(settings.migration_database_url)
    try:
        with database.sessions() as session:
            result = create_account(session, payload, role=args.role)
        print(
            f"Created {result.role} account {result.id}; no password or token was printed"
        )
    except AccountExists:
        raise SystemExit(
            "Account already exists; no existing role was changed"
        ) from None
    except SQLAlchemyError:
        raise SystemExit(
            "Database operation failed; check migration/configuration"
        ) from None
    finally:
        database.dispose()


if __name__ == "__main__":
    main()
```

### app/core/__init__.py

```python
"""Application configuration and infrastructure concerns."""
```

### app/core/config.py

```python
"""Load and validate application settings without storing secrets in code."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from sqlalchemy.engine import make_url
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Environment variables override values in the backend's local .env."""

    app_name: str = Field(default="DailyDabba API", min_length=1)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    database_url: SecretStr | None = Field(default=None, repr=False)
    migration_database_url: SecretStr | None = Field(default=None, repr=False)
    test_database_url: SecretStr | None = Field(default=None, repr=False)

    jwt_secret: SecretStr | None = Field(default=None, repr=False)
    jwt_issuer: str = Field(default="dailydabba-api", min_length=1, max_length=120)
    jwt_audience: str = Field(
        default="dailydabba-clients", min_length=1, max_length=120
    )
    access_token_minutes: int = Field(default=15, ge=1, le=60)
    auth_rate_limit_per_minute: int = Field(default=10, ge=1, le=1000)

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, value: SecretStr | None) -> SecretStr | None:
        if value is not None:
            secret = value.get_secret_value()
            if len(secret.encode("utf-8")) < 32 or secret.startswith("replace_"):
                raise ValueError(
                    "JWT_SECRET must be a generated secret of at least 32 bytes"
                )
        return value

    @field_validator("database_url", "migration_database_url", "test_database_url")
    @classmethod
    def validate_postgres_url(cls, value: SecretStr | None) -> SecretStr | None:
        if value is None:
            return None
        try:
            url = make_url(value.get_secret_value())
        except Exception:
            raise ValueError("Use a valid PostgreSQL connection URL") from None
        if (
            url.drivername != "postgresql+psycopg"
            or not url.host
            or not url.database
            or not url.username
            or not url.password
        ):
            raise ValueError(
                "Use postgresql+psycopg with host, database, user and password"
            )
        return value

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="forbid",
        hide_input_in_errors=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Validate settings once per server process."""
    return Settings()
```

### app/core/errors.py

```python
"""Safe API error responses; never echo validation inputs or SQL parameters."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import AuthNotConfigured, InvalidCredentials
from app.services.auth import AccountExists
from app.services.profiles import ProfileNameRequired

logger = logging.getLogger(__name__)


def install_error_handlers(application: FastAPI) -> None:
    @application.exception_handler(RequestValidationError)
    async def invalid_input(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "detail": [
                    {"loc": list(item["loc"]), "type": item["type"], "msg": item["msg"]}
                    for item in error.errors()
                ]
            },
        )

    @application.exception_handler(InvalidCredentials)
    async def invalid_credentials(
        request: Request, error: InvalidCredentials
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or expired credentials"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @application.exception_handler(AuthNotConfigured)
    async def unavailable_auth(
        request: Request, error: AuthNotConfigured
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503, content={"detail": "Authentication unavailable"}
        )

    @application.exception_handler(AccountExists)
    async def duplicate_account(request: Request, error: AccountExists) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": "An account already exists for this email"},
        )

    @application.exception_handler(ProfileNameRequired)
    async def profile_name_required(
        request: Request, error: ProfileNameRequired
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": "full_name is required to create a profile"},
        )

    @application.exception_handler(SQLAlchemyError)
    async def database_error(request: Request, error: SQLAlchemyError) -> JSONResponse:
        logger.error("Database request failed")
        return JSONResponse(status_code=503, content={"detail": "Database unavailable"})
```

### app/core/logging.py

```python
"""Console logging with UTC timestamps."""

import logging
import time
from logging.config import dictConfig


class UTCFormatter(logging.Formatter):
    """Format timestamps in UTC, independently of the host's timezone."""

    converter = time.gmtime


def configure_logging(level: str) -> None:
    """Send application and Uvicorn logs to one console handler."""
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": UTCFormatter,
                    "format": "%(asctime)sZ %(levelname)s %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {"handlers": ["console"], "level": level},
            "loggers": {
                "uvicorn": {"handlers": [], "propagate": True},
                "uvicorn.error": {"handlers": [], "propagate": True},
                "uvicorn.access": {"handlers": [], "propagate": True},
            },
        }
    )
```

### app/core/rate_limit.py

```python
"""Bounded process-local throttling keyed by the ASGI client address."""

import math
from collections import deque
from collections.abc import Callable
from threading import Lock
from time import monotonic


class AuthRateLimiter:
    def __init__(self, limit: int, clock: Callable[[], float] = monotonic) -> None:
        self.limit = limit
        self.clock = clock
        self.events: dict[str, deque[float]] = {}
        self.lock = Lock()

    def retry_after(self, key: str) -> int | None:
        with self.lock:
            now = self.clock()
            for old_key in list(self.events):
                queue = self.events[old_key]
                while queue and queue[0] <= now - 60:
                    queue.popleft()
                if not queue:
                    del self.events[old_key]
            if key not in self.events and len(self.events) >= 4096:
                return 60
            queue = self.events.setdefault(key, deque())
            if len(queue) >= self.limit:
                return max(1, math.ceil(60 - (now - queue[0])))
            queue.append(now)
            return None
```

### app/core/security.py

```python
"""Argon2 password hashing and strictly verified short-lived JWT access tokens."""

import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from app.core.config import Settings

_password_hash = PasswordHash.recommended()
_dummy_hash = _password_hash.hash(secrets.token_urlsafe(32))


class InvalidCredentials(Exception):
    pass


class AuthNotConfigured(Exception):
    pass


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, stored_hash: str | None) -> tuple[bool, str | None]:
    """Unknown emails still incur a real Argon2 check; malformed hashes fail closed."""
    try:
        valid, updated = _password_hash.verify_and_update(
            password, stored_hash or _dummy_hash
        )
    except (UnknownHashError, ValueError):
        _password_hash.verify(password, _dummy_hash)
        return False, None
    return valid and bool(stored_hash), updated


def require_signing_key(settings: Settings) -> str:
    if settings.jwt_secret is None:
        raise AuthNotConfigured()
    return settings.jwt_secret.get_secret_value()


def create_access_token(user_id: UUID, settings: Settings) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user_id),
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=settings.access_token_minutes),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "jti": str(uuid4()),
            "token_type": "access",
        },
        require_signing_key(settings),
        algorithm="HS256",
    )


def decode_access_token(token: str, settings: Settings) -> UUID:
    key = require_signing_key(settings)
    try:
        if len(token) > 4096:
            raise InvalidCredentials()
        payload = jwt.decode(
            token,
            key,
            algorithms=["HS256"],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={
                "require": [
                    "sub",
                    "iat",
                    "nbf",
                    "exp",
                    "iss",
                    "aud",
                    "jti",
                    "token_type",
                ]
            },
        )
        if payload["token_type"] != "access":
            raise InvalidCredentials()
        UUID(payload["jti"])
        return UUID(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError, KeyError):
        raise InvalidCredentials() from None
```

### app/db/__init__.py

```python
"""Database engines, scoped sessions, checks and offline schema tools.

Table changes run only through explicit Alembic commands, never on import or
application startup. Provisioning is a separate, explicitly invoked admin tool.
"""
```

### app/db/base.py

```python
"""Declarative metadata only: importing models never opens a connection."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(table_name)s_%(column_0_N_name)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class Record:
    """UUIDs are generated on ORM insert; all creation instants use timestamptz."""

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
```

### app/db/check.py

```python
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
```

### app/db/database.py

```python
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
```

### app/db/export_schema.py

```python
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
```

### app/db/provision.py

```python
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
```

### app/main.py

```python
"""FastAPI application entry point."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.core.errors import install_error_handlers
from app.core.rate_limit import AuthRateLimiter
from app.db.database import Database

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build one application; tests may supply isolated settings."""
    settings = settings if settings is not None else get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        configure_logging(settings.log_level)
        application.state.database = (
            Database.from_url(settings.database_url) if settings.database_url else None
        )
        logger.info("DailyDabba backend started")
        try:
            yield
        finally:
            if application.state.database is not None:
                application.state.database.dispose()
            logger.info("DailyDabba backend stopped")

    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        debug=False,
    )
    application.state.settings = settings
    application.state.auth_limiter = AuthRateLimiter(
        settings.auth_rate_limit_per_minute
    )
    install_error_handlers(application)

    @application.middleware("http")
    async def prevent_api_caching(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    application.include_router(api_router)
    return application


app = create_app()
```

### app/models/__init__.py

```python
"""Import all mappings so Base.metadata includes the complete Phase 3 design."""

from app.models.catalog import DailyMenu, FoodCategory, FoodItem, MenuItem
from app.models.commerce import Cart, CartItem, DeliverySlot, Order, OrderItem
from app.models.identity import Address, CustomerProfile, User
from app.models.operations import AuditLog, KitchenOrder, Notification
from app.models.payments import Payment, PaymentWebhookEvent, Refund
from app.models.subscriptions import (
    CreditAccount,
    CreditTransaction,
    Subscription,
    SubscriptionEvent,
    SubscriptionPlan,
)

__all__ = [
    "Address",
    "AuditLog",
    "Cart",
    "CartItem",
    "CreditAccount",
    "CreditTransaction",
    "CustomerProfile",
    "DailyMenu",
    "DeliverySlot",
    "FoodCategory",
    "FoodItem",
    "KitchenOrder",
    "MenuItem",
    "Notification",
    "Order",
    "OrderItem",
    "Payment",
    "PaymentWebhookEvent",
    "Refund",
    "Subscription",
    "SubscriptionEvent",
    "SubscriptionPlan",
    "User",
]
```

### app/models/catalog.py

```python
"""Catalog prices and dated, meal-specific kitchen offerings."""

from datetime import date
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, Record

MEAL_CHECK = "meal_type IN ('breakfast', 'lunch', 'dinner')"


class FoodCategory(Record, Base):
    __tablename__ = "food_categories"

    name: Mapped[str] = mapped_column(String(80), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    items: Mapped[list["FoodItem"]] = relationship(
        back_populates="category", passive_deletes="all"
    )


class FoodItem(Record, Base):
    __tablename__ = "food_items"
    __table_args__ = (CheckConstraint("price_paise >= 0", name="price_nonnegative"),)

    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("food_categories.id", ondelete="RESTRICT"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    price_paise: Mapped[int] = mapped_column(BigInteger)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=False)
    category: Mapped[FoodCategory] = relationship(back_populates="items")


class DailyMenu(Record, Base):
    __tablename__ = "daily_menus"
    __table_args__ = (
        UniqueConstraint("business_date", "meal_type"),
        UniqueConstraint("id", "business_date", "meal_type"),
        CheckConstraint(MEAL_CHECK, name="meal_type"),
    )

    business_date: Mapped[date] = mapped_column(Date)
    meal_type: Mapped[str] = mapped_column(String(12))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    items: Mapped[list["MenuItem"]] = relationship(
        back_populates="menu", passive_deletes="all"
    )


class MenuItem(Record, Base):
    __tablename__ = "menu_items"
    __table_args__ = (
        UniqueConstraint("menu_id", "food_item_id"),
        UniqueConstraint("id", "menu_id"),
        CheckConstraint("price_paise >= 0", name="price_nonnegative"),
        CheckConstraint("portions_remaining >= 0", name="stock_nonnegative"),
    )

    menu_id: Mapped[UUID] = mapped_column(
        ForeignKey("daily_menus.id", ondelete="RESTRICT"), index=True
    )
    food_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("food_items.id", ondelete="RESTRICT"), index=True
    )
    price_paise: Mapped[int] = mapped_column(BigInteger)
    portions_remaining: Mapped[int] = mapped_column(Integer, default=0)
    is_available: Mapped[bool] = mapped_column(Boolean, default=False)
    menu: Mapped[DailyMenu] = relationship(back_populates="items")
    food_item: Mapped[FoodItem] = relationship()
```

### app/models/commerce.py

```python
"""Carts and order snapshots; no checkout or status-transition services yet."""

from datetime import date, datetime, time
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Computed,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, Record
from app.models.catalog import MEAL_CHECK


class DeliverySlot(Record, Base):
    __tablename__ = "delivery_slots"
    __table_args__ = (
        UniqueConstraint("meal_type", "start_local", "end_local"),
        UniqueConstraint("id", "meal_type"),
        CheckConstraint(MEAL_CHECK, name="meal_type"),
        CheckConstraint("end_local > start_local", name="time_window"),
    )

    name: Mapped[str] = mapped_column(String(80))
    meal_type: Mapped[str] = mapped_column(String(12))
    start_local: Mapped[time] = mapped_column(Time(timezone=False))
    end_local: Mapped[time] = mapped_column(Time(timezone=False))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Cart(Record, Base):
    __tablename__ = "carts"
    __table_args__ = (UniqueConstraint("id", "menu_id"),)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), unique=True
    )
    menu_id: Mapped[UUID] = mapped_column(
        ForeignKey("daily_menus.id", ondelete="RESTRICT"), index=True
    )
    items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart", passive_deletes="all"
    )


class CartItem(Record, Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        ForeignKeyConstraint(
            ["cart_id", "menu_id"], ["carts.id", "carts.menu_id"], ondelete="CASCADE"
        ),
        ForeignKeyConstraint(
            ["menu_item_id", "menu_id"],
            ["menu_items.id", "menu_items.menu_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("cart_id", "menu_item_id"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
    )

    cart_id: Mapped[UUID] = mapped_column(index=True)
    menu_id: Mapped[UUID] = mapped_column(index=True)
    menu_item_id: Mapped[UUID] = mapped_column(index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    cart: Mapped[Cart] = relationship(back_populates="items")


class Order(Record, Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        UniqueConstraint("id", "menu_id"),
        UniqueConstraint("user_id", "idempotency_key"),
        ForeignKeyConstraint(
            ["address_id", "user_id"],
            ["addresses.id", "addresses.user_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["menu_id", "business_date", "meal_type"],
            ["daily_menus.id", "daily_menus.business_date", "daily_menus.meal_type"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["delivery_slot_id", "meal_type"],
            ["delivery_slots.id", "delivery_slots.meal_type"],
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "subtotal_paise >= 0 AND delivery_fee_paise >= 0 AND tax_paise >= 0 AND discount_paise >= 0 AND total_paise >= 0",
            name="amounts_nonnegative",
        ),
        CheckConstraint(
            "total_paise = subtotal_paise + delivery_fee_paise + tax_paise - discount_paise",
            name="total_equation",
        ),
        CheckConstraint("delivery_end_at > delivery_start_at", name="delivery_window"),
        CheckConstraint(
            "business_date = (delivery_start_at AT TIME ZONE 'Asia/Kolkata')::date AND business_date = (delivery_end_at AT TIME ZONE 'Asia/Kolkata')::date",
            name="business_date_local",
        ),
        CheckConstraint(
            "jsonb_typeof(address_snapshot) = 'object'", name="address_object"
        ),
        CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name="request_identity",
        ),
        CheckConstraint(
            "status IN ('pending_payment', 'placed', 'confirmed', 'preparing', 'ready', 'out_for_delivery', 'delivered', 'cancelled')",
            name="status",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    address_id: Mapped[UUID] = mapped_column(index=True)
    address_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB)
    menu_id: Mapped[UUID] = mapped_column(index=True)
    business_date: Mapped[date] = mapped_column(Date, index=True)
    meal_type: Mapped[str] = mapped_column(String(12))
    delivery_slot_id: Mapped[UUID] = mapped_column(index=True)
    delivery_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    delivery_end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    subtotal_paise: Mapped[int] = mapped_column(BigInteger)
    delivery_fee_paise: Mapped[int] = mapped_column(BigInteger)
    tax_paise: Mapped[int] = mapped_column(BigInteger)
    discount_paise: Mapped[int] = mapped_column(BigInteger)
    total_paise: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(
        String(24), default="pending_payment", index=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(128))
    request_hash: Mapped[str] = mapped_column(String(64))
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", passive_deletes="all"
    )


class OrderItem(Record, Base):
    __tablename__ = "order_items"
    __table_args__ = (
        ForeignKeyConstraint(
            ["order_id", "menu_id"],
            ["orders.id", "orders.menu_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["menu_item_id", "menu_id"],
            ["menu_items.id", "menu_items.menu_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("order_id", "menu_item_id"),
        CheckConstraint("quantity > 0 AND unit_price_paise >= 0", name="item_amount"),
    )

    order_id: Mapped[UUID] = mapped_column(index=True)
    menu_id: Mapped[UUID] = mapped_column(index=True)
    menu_item_id: Mapped[UUID] = mapped_column(index=True)
    food_name: Mapped[str] = mapped_column(String(120))
    unit_price_paise: Mapped[int] = mapped_column(BigInteger)
    quantity: Mapped[int] = mapped_column(Integer)
    line_total_paise: Mapped[int] = mapped_column(
        BigInteger, Computed("unit_price_paise * quantity", persisted=True)
    )
    order: Mapped[Order] = relationship(back_populates="items")
```

### app/models/identity.py

```python
"""Accounts, private profile data and soft-deletable address book entries."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, Record


class User(Record, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "email = lower(email) AND length(email) > 3", name="email_normalized"
        ),
        CheckConstraint("role IN ('customer', 'admin', 'kitchen_staff')", name="role"),
    )

    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    role: Mapped[str] = mapped_column(String(20), default="customer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    profile: Mapped["CustomerProfile | None"] = relationship(back_populates="user")
    addresses: Mapped[list["Address"]] = relationship(
        back_populates="user", passive_deletes="all"
    )


class CustomerProfile(Record, Base):
    __tablename__ = "customer_profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), unique=True
    )
    full_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str | None] = mapped_column(String(20))
    user: Mapped[User] = relationship(back_populates="profile")


class Address(Record, Base):
    __tablename__ = "addresses"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        CheckConstraint("length(postal_code) = 6", name="postal_code_length"),
        CheckConstraint(
            "NOT is_default OR deleted_at IS NULL", name="default_not_deleted"
        ),
        Index(
            "uq_addresses_one_live_default",
            "user_id",
            unique=True,
            postgresql_where=text("is_default AND deleted_at IS NULL"),
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    label: Mapped[str] = mapped_column(String(50))
    recipient_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(20))
    line1: Mapped[str] = mapped_column(String(200))
    line2: Mapped[str | None] = mapped_column(String(200))
    locality: Mapped[str] = mapped_column(String(120))
    city: Mapped[str] = mapped_column(String(80))
    state: Mapped[str] = mapped_column(String(80))
    postal_code: Mapped[str] = mapped_column(String(6))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user: Mapped[User] = relationship(back_populates="addresses")
```

### app/models/operations.py

```python
"""Kitchen work, notifications and minimal audit evidence."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Record


class KitchenOrder(Record, Base):
    __tablename__ = "kitchen_orders"
    __table_args__ = (
        CheckConstraint(
            "status IN ('queued', 'preparing', 'ready', 'completed', 'cancelled')",
            name="status",
        ),
    )

    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="RESTRICT"), unique=True
    )
    status: Mapped[str] = mapped_column(String(16), default="queued", index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Notification(Record, Base):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint("channel IN ('in_app', 'email', 'sms')", name="channel"),
        CheckConstraint(
            "status IN ('pending', 'sent', 'failed', 'read')", name="status"
        ),
        CheckConstraint("jsonb_typeof(payload) = 'object'", name="payload_object"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    event_key: Mapped[str] = mapped_column(String(150), unique=True)
    channel: Mapped[str] = mapped_column(String(12))
    status: Mapped[str] = mapped_column(String(12), default="pending", index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuditLog(Record, Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        CheckConstraint("jsonb_typeof(details) = 'object'", name="details_object"),
    )

    actor_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    action: Mapped[str] = mapped_column(String(100))
    target_type: Mapped[str] = mapped_column(String(80))
    target_id: Mapped[UUID] = mapped_column(index=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSONB)
```

### app/models/payments.py

```python
"""Payment evidence, refund requests and deduplicated provider event records."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Record


class Payment(Record, Base):
    __tablename__ = "payments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["order_id", "user_id"],
            ["orders.id", "orders.user_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["subscription_id", "user_id"],
            ["subscriptions.id", "subscriptions.user_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("user_id", "idempotency_key"),
        UniqueConstraint("provider", "provider_payment_id"),
        CheckConstraint(
            "(order_id IS NOT NULL AND subscription_id IS NULL) OR (order_id IS NULL AND subscription_id IS NOT NULL)",
            name="one_target",
        ),
        CheckConstraint(
            "amount_paise > 0 AND currency = 'INR'", name="amount_currency"
        ),
        CheckConstraint("provider = 'razorpay'", name="provider"),
        CheckConstraint(
            "status IN ('created', 'authorized', 'captured', 'failed')", name="status"
        ),
        CheckConstraint(
            "(status = 'captured') = (captured_at IS NOT NULL)", name="capture_instant"
        ),
        CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name="request_identity",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    order_id: Mapped[UUID | None] = mapped_column(index=True)
    subscription_id: Mapped[UUID | None] = mapped_column(index=True)
    amount_paise: Mapped[int] = mapped_column(BigInteger)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    provider: Mapped[str] = mapped_column(String(20), default="razorpay")
    provider_order_id: Mapped[str | None] = mapped_column(String(100), index=True)
    provider_payment_id: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(16), default="created", index=True)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    request_hash: Mapped[str] = mapped_column(String(64))


class Refund(Record, Base):
    __tablename__ = "refunds"
    __table_args__ = (
        UniqueConstraint("payment_id", "idempotency_key"),
        UniqueConstraint("provider_refund_id"),
        CheckConstraint("amount_paise > 0", name="amount_positive"),
        CheckConstraint(
            "status IN ('requested', 'processing', 'succeeded', 'failed')",
            name="status",
        ),
        CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name="request_identity",
        ),
    )

    payment_id: Mapped[UUID] = mapped_column(
        ForeignKey("payments.id", ondelete="RESTRICT"), index=True
    )
    amount_paise: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(16), default="requested")
    reason: Mapped[str] = mapped_column(String(300))
    provider_refund_id: Mapped[str | None] = mapped_column(String(100))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    request_hash: Mapped[str] = mapped_column(String(64))


class PaymentWebhookEvent(Record, Base):
    __tablename__ = "payment_webhook_events"
    __table_args__ = (
        UniqueConstraint("provider", "provider_event_id"),
        CheckConstraint("provider = 'razorpay'", name="provider"),
        CheckConstraint("status IN ('received', 'processed', 'failed')", name="status"),
        CheckConstraint(
            "length(provider_event_id) > 0 AND length(payload_hash) = 64",
            name="event_identity",
        ),
        CheckConstraint(
            "jsonb_typeof(sanitized_payload) = 'object'", name="payload_object"
        ),
    )

    provider: Mapped[str] = mapped_column(String(20), default="razorpay")
    provider_event_id: Mapped[str] = mapped_column(String(150))
    payment_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("payments.id", ondelete="RESTRICT"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(100))
    payload_hash: Mapped[str] = mapped_column(String(64))
    sanitized_payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(16), default="received", index=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
```

### app/models/subscriptions.py

```python
"""Subscription terms, lifecycle history and an auditable credit ledger."""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, Record
from app.models.catalog import MEAL_CHECK


class SubscriptionPlan(Record, Base):
    __tablename__ = "subscription_plans"
    __table_args__ = (
        CheckConstraint("period IN ('weekly', 'monthly')", name="period"),
        CheckConstraint(MEAL_CHECK, name="meal_type"),
        CheckConstraint(
            "duration_days > 0 AND included_credits > 0 AND price_paise >= 0",
            name="terms_positive",
        ),
    )

    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    period: Mapped[str] = mapped_column(String(12))
    meal_type: Mapped[str] = mapped_column(String(12))
    duration_days: Mapped[int] = mapped_column(Integer)
    included_credits: Mapped[int] = mapped_column(Integer)
    price_paise: Mapped[int] = mapped_column(BigInteger)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)


class Subscription(Record, Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("id", "user_id"),
        ForeignKeyConstraint(
            ["renewed_from_id", "user_id"],
            ["subscriptions.id", "subscriptions.user_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("user_id", "idempotency_key"),
        CheckConstraint("expires_on > starts_on", name="date_window"),
        CheckConstraint(
            "purchased_credits > 0 AND price_paise >= 0", name="purchased_terms"
        ),
        CheckConstraint(MEAL_CHECK, name="meal_type"),
        CheckConstraint(
            "status IN ('pending_payment', 'active', 'paused', 'expired', 'cancelled')",
            name="status",
        ),
        CheckConstraint(
            "jsonb_typeof(policy_snapshot) = 'object'", name="policy_object"
        ),
        CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name="request_identity",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("subscription_plans.id", ondelete="RESTRICT"), index=True
    )
    renewed_from_id: Mapped[UUID | None] = mapped_column(index=True)
    plan_name: Mapped[str] = mapped_column(String(120))
    meal_type: Mapped[str] = mapped_column(String(12))
    purchased_credits: Mapped[int] = mapped_column(Integer)
    price_paise: Mapped[int] = mapped_column(BigInteger)
    starts_on: Mapped[date] = mapped_column(Date)
    expires_on: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(20), default="pending_payment", index=True
    )
    policy_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB)
    idempotency_key: Mapped[str] = mapped_column(String(128))
    request_hash: Mapped[str] = mapped_column(String(64))


class SubscriptionEvent(Record, Base):
    __tablename__ = "subscription_events"
    __table_args__ = (
        UniqueConstraint("subscription_id", "event_key"),
        CheckConstraint(
            "event_type IN ('activate', 'pause', 'resume', 'skip', 'renew', 'expire', 'cancel')",
            name="event_type",
        ),
        CheckConstraint("length(event_key) > 0", name="event_key"),
        Index(
            "uq_subscription_skip_date",
            "subscription_id",
            "effective_date",
            unique=True,
            postgresql_where=text("event_type = 'skip'"),
        ),
    )

    subscription_id: Mapped[UUID] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="RESTRICT"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(16))
    effective_date: Mapped[date] = mapped_column(Date)
    event_key: Mapped[str] = mapped_column(String(128))
    reason: Mapped[str] = mapped_column(String(300))
    actor_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )


class CreditAccount(Record, Base):
    __tablename__ = "subscription_credits"
    __table_args__ = (
        ForeignKeyConstraint(
            ["subscription_id", "user_id"],
            ["subscriptions.id", "subscriptions.user_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "user_id"),
        CheckConstraint("balance >= 0", name="balance_nonnegative"),
    )

    subscription_id: Mapped[UUID] = mapped_column(unique=True)
    user_id: Mapped[UUID] = mapped_column(index=True)
    balance: Mapped[int] = mapped_column(Integer, default=0)


class CreditTransaction(Record, Base):
    __tablename__ = "credit_transactions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["account_id", "user_id"],
            ["subscription_credits.id", "subscription_credits.user_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["order_id", "user_id"],
            ["orders.id", "orders.user_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("account_id", "event_key"),
        Index(
            "uq_credit_account_purchase_grant",
            "account_id",
            unique=True,
            postgresql_where=text("kind = 'grant'"),
        ),
        UniqueConstraint("account_id", "order_id", "kind"),
        CheckConstraint("delta <> 0", name="delta_nonzero"),
        CheckConstraint(
            "kind IN ('grant', 'debit', 'restore', 'expire', 'adjust')", name="kind"
        ),
        CheckConstraint(
            "(kind IN ('grant', 'restore') AND delta > 0) OR (kind IN ('debit', 'expire') AND delta < 0) OR kind = 'adjust'",
            name="delta_direction",
        ),
        CheckConstraint(
            "kind NOT IN ('debit', 'restore') OR order_id IS NOT NULL",
            name="order_required",
        ),
        CheckConstraint(
            "length(event_key) > 0 AND length(request_hash) = 64 AND length(reason) > 0",
            name="event_identity",
        ),
    )

    account_id: Mapped[UUID] = mapped_column(index=True)
    user_id: Mapped[UUID] = mapped_column(index=True)
    order_id: Mapped[UUID | None] = mapped_column(index=True)
    kind: Mapped[str] = mapped_column(String(12))
    delta: Mapped[int] = mapped_column(Integer)
    event_key: Mapped[str] = mapped_column(String(128))
    request_hash: Mapped[str] = mapped_column(String(64))
    reason: Mapped[str] = mapped_column(String(300))
    actor_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
```

### app/repositories/__init__.py

```python
"""SQLAlchemy queries and persistence operations, starting with user accounts.

Repositories receive a session from their caller. They make no HTTP decisions
and never independently commit a service transaction.
"""
```

### app/repositories/users.py

```python
"""User persistence; no HTTP decisions and no independent commits."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, selectinload

from app.models.identity import User


def by_email(session: Session, email: str) -> User | None:
    return session.scalar(
        select(User).where(User.email == email).options(selectinload(User.profile))
    )


def by_id(session: Session, user_id: UUID) -> User | None:
    return session.scalar(
        select(User).where(User.id == user_id).options(selectinload(User.profile))
    )


def insert_account(
    session: Session, *, email: str, password_hash: str, role: str
) -> User | None:
    """Unique email handles concurrent registration without a pre-check race."""
    return session.scalar(
        insert(User)
        .values(
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
        )
        .on_conflict_do_nothing(index_elements=[User.email])
        .returning(User)
    )
```

### app/schemas/__init__.py

```python
"""Validated API request and response contracts."""
```

### app/schemas/auth.py

```python
"""Authentication input/output contracts; passwords are write-only secrets."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    StringConstraints,
    model_validator,
)

Role = Literal["customer", "admin", "kitchen_staff"]
Name = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)
]
Phone = Annotated[str, StringConstraints(pattern=r"^\+[1-9][0-9]{7,14}$")]


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr = Field(max_length=254)
    password: SecretStr = Field(min_length=12, max_length=128)
    full_name: Name
    phone: Phone | None = None


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr = Field(max_length=254)
    password: SecretStr = Field(min_length=1, max_length=128)


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: Name | None = None
    phone: Phone | None = None

    @model_validator(mode="after")
    def valid_update(self) -> "ProfileUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide full_name or phone")
        if "full_name" in self.model_fields_set and self.full_name is None:
            raise ValueError("full_name cannot be null")
        return self


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    full_name: str
    phone: str | None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    role: Role
    is_active: bool
    created_at: datetime
    profile: ProfileResponse | None


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class AccessResponse(BaseModel):
    status: Literal["allowed"] = "allowed"
    role: Role
```

### app/schemas/health.py

```python
"""The public health-response contract."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Keep the health response small and free of sensitive configuration."""

    status: Literal["ok"]


class ReadinessResponse(BaseModel):
    """Database connectivity/configuration and migration readiness contract."""

    status: Literal["ready"]
```

### app/services/__init__.py

```python
"""Business use cases and transaction coordination.

Authentication and profile services own complete commits and call repositories.
Services do not depend on FastAPI route or HTTP request/response objects.
"""
```

### app/services/auth.py

```python
"""Account and authentication use cases own their transactions."""

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import (
    InvalidCredentials,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.identity import CustomerProfile
from app.models.operations import AuditLog
from app.repositories import users
from app.schemas.auth import RegisterRequest, TokenResponse, UserResponse


class AccountExists(Exception):
    pass


def create_account(
    session: Session, payload: RegisterRequest, *, role: str = "customer"
) -> UserResponse:
    """Only trusted code supplies role; the public route always calls register()."""
    if role not in {"customer", "admin", "kitchen_staff"}:
        raise ValueError("Unsupported role")
    password_hash = hash_password(payload.password.get_secret_value())
    with session.begin():
        user = users.insert_account(
            session,
            email=str(payload.email).lower(),
            password_hash=password_hash,
            role=role,
        )
        if user is None:
            raise AccountExists()
        user.profile = CustomerProfile(
            user_id=user.id, full_name=payload.full_name, phone=payload.phone
        )
        session.add(
            AuditLog(
                actor_user_id=None,
                action=(
                    "account_registered"
                    if role == "customer"
                    else "staff_account_created"
                ),
                target_type="users",
                target_id=user.id,
                details={"role": role},
            )
        )
        session.flush()
        response = UserResponse.model_validate(user)
    return response


def register(session: Session, payload: RegisterRequest) -> UserResponse:
    return create_account(session, payload, role="customer")


def login(
    session: Session, email: str, password: str, settings: Settings
) -> TokenResponse:
    with session.begin():
        user = users.by_email(session, email.lower())
        valid, upgraded_hash = verify_password(
            password, user.password_hash if user else None
        )
        if (
            not valid
            or user is None
            or not user.is_active
            or user.deactivated_at is not None
        ):
            raise InvalidCredentials()
        if upgraded_hash:
            user.password_hash = upgraded_hash
        token = create_access_token(user.id, settings)
    return TokenResponse(
        access_token=token, expires_in=settings.access_token_minutes * 60
    )
```

### app/services/profiles.py

```python
"""Update only the authenticated user's permitted profile fields."""

from sqlalchemy.orm import Session

from app.models.identity import CustomerProfile, User
from app.models.operations import AuditLog
from app.schemas.auth import ProfileUpdate, UserResponse


class ProfileNameRequired(Exception):
    pass


def update_profile(
    session: Session, user: User, payload: ProfileUpdate
) -> UserResponse:
    if user.profile is None:
        if payload.full_name is None:
            raise ProfileNameRequired()
        user.profile = CustomerProfile(user_id=user.id, full_name=payload.full_name)
    for field in payload.model_fields_set:
        setattr(user.profile, field, getattr(payload, field))
    session.add(
        AuditLog(
            actor_user_id=user.id,
            action="profile_updated",
            target_type="users",
            target_id=user.id,
            details={"fields": sorted(payload.model_fields_set)},
        )
    )
    # The current-user lookup already started this request's transaction.
    session.flush()
    response = UserResponse.model_validate(user)
    session.commit()
    return response
```

### app/tests/__init__.py

```python
"""Backend automated checks."""
```

### app/tests/conftest.py

```python
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
```

### app/tests/test_auth_integration.py

```python
"""Registration/login/profile/RBAC through real HTTP handlers and runtime DB role."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import func, select, text, update
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings
from app.core.security import create_access_token, verify_password
from app.main import create_app
from app.models.identity import CustomerProfile, User
from app.models.operations import AuditLog
from app.schemas.auth import RegisterRequest
from app.services import auth as auth_service

pytestmark = pytest.mark.database
PASSWORD = "Only-for-tests-long-password!"


@pytest.fixture
def auth_api(databases):
    migration, runtime, _ = databases
    # The shared fixture verified actual current_database() == dailydabba_test.
    from app.db.base import Base

    tables = ", ".join('public."' + name + '"' for name in Base.metadata.tables)

    def clean():
        with migration.engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE " + tables + " CASCADE"))

    clean()
    settings = Settings(
        _env_file=None,
        database_url=SecretStr(
            runtime.engine.url.render_as_string(hide_password=False)
        ),
        jwt_secret=SecretStr("integration-test-signing-key-at-least-32-bytes"),
        auth_rate_limit_per_minute=500,
    )
    application = create_app(settings)
    try:
        with TestClient(application) as client:
            yield client, migration, settings
    finally:
        clean()


def register(client, email=None, **overrides):
    data = {
        "email": email or f"user-{uuid4().hex}@example.com",
        "password": PASSWORD,
        "full_name": " Test Customer ",
        "phone": "+919876543210",
    }
    data.update(overrides)
    return client.post("/api/v1/auth/register", json=data)


def login(client, email, password=PASSWORD):
    return client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )


def headers(client, email):
    response = login(client, email)
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response.json()["access_token"]}


def test_registration_is_canonical_atomic_and_never_returns_password(auth_api):
    client, database, _ = auth_api
    email = f"MiXeD-{uuid4().hex}@EXAMPLE.COM"
    response = register(client, email)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == email.lower()
    assert body["role"] == "customer" and body["is_active"]
    assert body["profile"] == {"full_name": "Test Customer", "phone": "+919876543210"}
    assert "password" not in response.text and PASSWORD not in response.text
    with database.sessions() as session:
        user = session.scalar(select(User).where(User.email == email.lower()))
        assert user.password_hash.startswith("$argon2id$")
        assert verify_password(PASSWORD, user.password_hash)[0]
        assert session.scalar(select(func.count()).select_from(CustomerProfile)) == 1
        assert session.scalar(select(func.count()).select_from(AuditLog)) == 1


def test_duplicate_registration_is_409_without_partial_records(auth_api):
    client, database, _ = auth_api
    email = f"duplicate-{uuid4().hex}@example.com"
    assert register(client, email).status_code == 201
    assert register(client, email.upper()).status_code == 409
    with database.sessions() as session:
        assert session.scalar(select(func.count()).select_from(User)) == 1
        assert session.scalar(select(func.count()).select_from(CustomerProfile)) == 1


@pytest.mark.parametrize(
    "field,value",
    [
        ("role", "admin"),
        ("is_active", True),
        ("password_hash", "attacker"),
        ("id", str(uuid4())),
    ],
)
def test_registration_cannot_assign_privileged_fields(auth_api, field, value):
    client, database, _ = auth_api
    assert register(client, **{field: value}).status_code == 422
    with database.sessions() as session:
        assert session.scalar(select(func.count()).select_from(User)) == 0


@pytest.mark.parametrize(
    "changes",
    [
        {"email": "invalid-email"},
        {"password": "tiny"},
        {"password": "x" * 129},
        {"full_name": "   "},
        {"phone": "invalid"},
    ],
)
def test_invalid_registration_inputs_do_not_create_accounts(auth_api, changes):
    client, database, _ = auth_api
    response = register(client, **changes)
    assert response.status_code == 422
    assert "input" not in response.text
    with database.sessions() as session:
        assert session.scalar(select(func.count()).select_from(User)) == 0


def test_login_has_generic_errors_and_short_lived_token(auth_api):
    client, _, settings = auth_api
    user = register(client).json()
    wrong = login(client, user["email"], "wrong password")
    unknown = login(client, "unknown@example.com", "wrong password")
    assert wrong.status_code == unknown.status_code == 401
    assert (
        wrong.json() == unknown.json() == {"detail": "Invalid or expired credentials"}
    )
    assert wrong.headers["www-authenticate"] == "Bearer"
    response = login(client, user["email"].upper())
    assert response.status_code == 200
    token = response.json()
    assert set(token) == {"access_token", "token_type", "expires_in"}
    assert token["expires_in"] == settings.access_token_minutes * 60
    assert token["token_type"] == "bearer"
    assert response.headers["cache-control"] == "no-store"
    claims = jwt.decode(
        token["access_token"],
        settings.jwt_secret.get_secret_value(),
        algorithms=["HS256"],
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
    )
    assert claims["sub"] == user["id"] and "role" not in claims
    assert claims["exp"] - claims["iat"] == settings.access_token_minutes * 60


def test_profile_only_updates_current_user_and_forbids_mass_assignment(auth_api):
    client, _, _ = auth_api
    one, two = register(client).json(), register(client).json()
    first, second = headers(client, one["email"]), headers(client, two["email"])
    assert client.get("/api/v1/users/me", headers=first).json()["id"] == one["id"]
    response = client.patch(
        "/api/v1/users/me/profile",
        headers=first,
        json={"full_name": "Private New Name", "phone": None},
    )
    assert response.status_code == 200
    assert response.json()["profile"] == {
        "full_name": "Private New Name",
        "phone": None,
    }
    assert (
        client.get("/api/v1/users/me", headers=second).json()["profile"]["full_name"]
        == "Test Customer"
    )
    for data in [
        {"role": "admin"},
        {"user_id": two["id"]},
        {"email": two["email"]},
        {"full_name": None},
        {},
    ]:
        assert (
            client.patch(
                "/api/v1/users/me/profile", headers=first, json=data
            ).status_code
            == 422
        )
    assert client.get("/api/v1/users/" + two["id"], headers=first).status_code == 404


@pytest.mark.parametrize(
    "role,admin,kitchen",
    [("customer", 403, 403), ("kitchen_staff", 403, 200), ("admin", 200, 200)],
)
def test_role_guards_with_real_password_login(auth_api, role, admin, kitchen):
    client, database, _ = auth_api
    email = f"role-{uuid4().hex}@example.com"
    with database.sessions() as session:
        auth_service.create_account(
            session,
            RegisterRequest(email=email, password=PASSWORD, full_name="Role Test"),
            role=role,
        )
    authorization = headers(client, email)
    assert (
        client.get("/api/v1/admin/access-check", headers=authorization).status_code
        == admin
    )
    assert (
        client.get("/api/v1/kitchen/access-check", headers=authorization).status_code
        == kitchen
    )


def test_current_database_role_overrides_stale_or_extra_token_role_claims(auth_api):
    client, database, settings = auth_api
    user = register(client).json()
    authorization = headers(client, user["email"])
    assert (
        client.get("/api/v1/admin/access-check", headers=authorization).status_code
        == 403
    )
    with database.engine.begin() as connection:
        connection.execute(
            update(User).where(User.email == user["email"]).values(role="admin")
        )
    assert (
        client.get("/api/v1/admin/access-check", headers=authorization).status_code
        == 200
    )
    with database.engine.begin() as connection:
        connection.execute(
            update(User).where(User.email == user["email"]).values(role="customer")
        )
    assert (
        client.get("/api/v1/admin/access-check", headers=authorization).status_code
        == 403
    )
    key = settings.jwt_secret.get_secret_value()
    claims = jwt.decode(
        authorization["Authorization"].split()[1],
        key,
        algorithms=["HS256"],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
    )
    claims["role"] = "admin"
    forged_role = {
        "Authorization": "Bearer " + jwt.encode(claims, key, algorithm="HS256")
    }
    assert (
        client.get("/api/v1/admin/access-check", headers=forged_role).status_code == 403
    )


@pytest.mark.parametrize(
    "change", [{"is_active": False}, {"deactivated_at": datetime.now(timezone.utc)}]
)
def test_deactivated_user_cannot_login_or_reuse_existing_token(auth_api, change):
    client, database, _ = auth_api
    user = register(client).json()
    authorization = headers(client, user["email"])
    with database.engine.begin() as connection:
        connection.execute(
            update(User).where(User.email == user["email"]).values(**change)
        )
    assert client.get("/api/v1/users/me", headers=authorization).status_code == 401
    assert login(client, user["email"]).status_code == 401


def test_signed_token_for_nonexistent_user_is_rejected(auth_api):
    client, _, settings = auth_api
    authorization = {
        "Authorization": "Bearer " + create_access_token(uuid4(), settings)
    }
    assert client.get("/api/v1/users/me", headers=authorization).status_code == 401


def test_registration_failure_rolls_back_and_sanitizes_database_error(
    auth_api, monkeypatch
):
    client, database, _ = auth_api
    original = auth_service.users.insert_account

    def fail_after_insert(*args, **kwargs):
        original(*args, **kwargs)
        raise SQLAlchemyError("sensitive SQL or password must never be returned")

    monkeypatch.setattr(auth_service.users, "insert_account", fail_after_insert)
    response = register(client)
    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
    with database.sessions() as session:
        assert session.scalar(select(func.count()).select_from(User)) == 0
        assert session.scalar(select(func.count()).select_from(CustomerProfile)) == 0


def test_simultaneous_registration_has_one_account_and_profile(auth_api):
    client, database, _ = auth_api
    email = f"race-{uuid4().hex}@example.com"
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: register(client, email), range(2)))
    assert sorted(response.status_code for response in responses) == [201, 409]
    with database.sessions() as session:
        assert session.scalar(select(func.count()).select_from(User)) == 1
        assert session.scalar(select(func.count()).select_from(CustomerProfile)) == 1


def test_profile_audit_contains_field_names_not_private_values(auth_api):
    client, database, _ = auth_api
    user = register(client).json()
    response = client.patch(
        "/api/v1/users/me/profile",
        headers=headers(client, user["email"]),
        json={"full_name": "Private Name Not For Audit"},
    )
    assert response.status_code == 200
    with database.sessions() as session:
        audit = session.scalar(
            select(AuditLog).where(AuditLog.action == "profile_updated")
        )
        assert audit.details == {"fields": ["full_name"]}
        assert PASSWORD not in str(audit.details)
        assert "Private Name Not For Audit" not in str(audit.details)


def test_older_argon2_parameters_are_upgraded_on_successful_login(auth_api):
    from argon2 import PasswordHasher

    client, database, _ = auth_api
    user = register(client).json()
    weaker = PasswordHasher(time_cost=1, memory_cost=8192, parallelism=1).hash(PASSWORD)
    with database.engine.begin() as connection:
        connection.execute(
            update(User).where(User.email == user["email"]).values(password_hash=weaker)
        )
    assert login(client, user["email"]).status_code == 200
    with database.sessions() as session:
        changed = session.scalar(select(User).where(User.email == user["email"]))
        assert changed.password_hash != weaker
        assert verify_password(PASSWORD, changed.password_hash)[0]


def test_staff_command_prompts_without_echoing_and_never_promotes_existing_account(
    auth_api, monkeypatch
):
    from app.cli import create_staff

    client, database, settings = auth_api
    trusted = settings.model_copy(
        update={
            "migration_database_url": SecretStr(
                database.engine.url.render_as_string(hide_password=False)
            )
        }
    )
    email = f"cli-{uuid4().hex}@example.com"
    monkeypatch.setattr(create_staff, "get_settings", lambda: trusted)
    monkeypatch.setattr(create_staff, "getpass", lambda prompt: PASSWORD)
    monkeypatch.setattr(
        "sys.argv",
        [
            "create_staff",
            "--email",
            email,
            "--full-name",
            "Local Staff",
            "--role",
            "admin",
        ],
    )
    from contextlib import redirect_stdout
    from io import StringIO
    captured = StringIO()
    with redirect_stdout(captured):
        create_staff.main()
    output = captured.getvalue()
    assert "Created admin account" in output
    assert PASSWORD not in output
    assert (
        client.get(
            "/api/v1/admin/access-check", headers=headers(client, email)
        ).status_code
        == 200
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "create_staff",
            "--email",
            email,
            "--full-name",
            "Local Staff",
            "--role",
            "kitchen_staff",
        ],
    )
    with pytest.raises(SystemExit, match="Account already exists"):
        create_staff.main()
    with database.sessions() as session:
        assert session.scalar(select(User.role).where(User.email == email)) == "admin"
```

### app/tests/test_config.py

```python
"""Reject invalid configuration and verify environment-variable precedence."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_environment_overrides_dotenv(monkeypatch, tmp_path) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text("APP_NAME=From file\nLOG_LEVEL=INFO\n", encoding="utf-8")
    monkeypatch.setenv("APP_NAME", "From environment")
    assert Settings(_env_file=dotenv).app_name == "From environment"


def test_invalid_log_level_fails_validation() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, log_level="INVALID")
```

### app/tests/test_database_integration.py

```python
"""Real PostgreSQL migration, constraint, permissions and session tests.

Run with --run-db. This resets dailydabba_test and never development data.
"""

import os
from datetime import date, datetime, time, timezone
from unittest.mock import patch
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import delete, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

import app.models as models
from app.core.config import BACKEND_ROOT, Settings, get_settings
from app.db.base import Base
from app.db.check import check_database
from app.db.database import Database, DbSession
from app.main import create_app

pytestmark = pytest.mark.database


@pytest.fixture
def session(databases):
    database, _, _ = databases
    with database.engine.connect() as connection:
        transaction = connection.begin()
        with Session(
            bind=connection, join_transaction_mode="create_savepoint"
        ) as session:
            try:
                yield session
            finally:
                session.close()
                transaction.rollback()


@pytest.fixture
def records(session):
    user = models.User(email="one@example.test", password_hash="test-only-hash")
    other = models.User(email="two@example.test", password_hash="test-only-hash")
    category = models.FoodCategory(name="test meals")
    menu = models.DailyMenu(business_date=date(2026, 11, 12), meal_type="lunch")
    slot = models.DeliverySlot(
        name="test slot", meal_type="lunch", start_local=time(12), end_local=time(13)
    )
    plan = models.SubscriptionPlan(
        code="TEST",
        name="test plan",
        period="weekly",
        meal_type="lunch",
        duration_days=7,
        included_credits=5,
        price_paise=25000,
    )
    session.add_all([user, other, category, menu, slot, plan])
    session.flush()
    address = models.Address(
        user_id=user.id,
        label="test",
        recipient_name="test",
        phone="0000000000",
        line1="test street",
        locality="test",
        city="Chennai",
        state="Tamil Nadu",
        postal_code="600001",
        is_default=True,
    )
    other_address = models.Address(
        user_id=other.id,
        label="test",
        recipient_name="test",
        phone="0000000000",
        line1="other street",
        locality="test",
        city="Chennai",
        state="Tamil Nadu",
        postal_code="600002",
    )
    food = models.FoodItem(
        category_id=category.id, name="test food", description="test", price_paise=5000
    )
    subscription = models.Subscription(
        user_id=user.id,
        plan_id=plan.id,
        plan_name=plan.name,
        meal_type="lunch",
        purchased_credits=5,
        price_paise=25000,
        starts_on=date(2026, 11, 12),
        expires_on=date(2026, 11, 19),
        policy_snapshot={"test": True},
        idempotency_key="sub-one",
        request_hash="a" * 64,
    )
    session.add_all([address, other_address, food, subscription])
    session.flush()
    item = models.MenuItem(
        menu_id=menu.id, food_item_id=food.id, price_paise=5000, portions_remaining=10
    )
    account = models.CreditAccount(
        subscription_id=subscription.id, user_id=user.id, balance=5
    )
    session.add_all([item, account])
    session.flush()
    order = models.Order(
        user_id=user.id,
        address_id=address.id,
        address_snapshot={"line1": address.line1},
        menu_id=menu.id,
        business_date=menu.business_date,
        meal_type="lunch",
        delivery_slot_id=slot.id,
        delivery_start_at=datetime(2026, 11, 12, 6, 30, tzinfo=timezone.utc),
        delivery_end_at=datetime(2026, 11, 12, 7, 30, tzinfo=timezone.utc),
        subtotal_paise=10000,
        delivery_fee_paise=0,
        tax_paise=0,
        discount_paise=0,
        total_paise=10000,
        idempotency_key="order-one",
        request_hash="b" * 64,
    )
    session.add(order)
    session.flush()
    line = models.OrderItem(
        order_id=order.id,
        menu_id=menu.id,
        menu_item_id=item.id,
        food_name=food.name,
        unit_price_paise=5000,
        quantity=2,
    )
    grant = models.CreditTransaction(
        account_id=account.id,
        user_id=user.id,
        kind="grant",
        delta=5,
        event_key="purchase",
        request_hash="c" * 64,
        reason="test purchase",
    )
    session.add_all([line, grant])
    session.flush()
    return dict(
        subscription=subscription,
        user=user,
        other=other,
        address=address,
        other_address=other_address,
        food=food,
        menu=menu,
        item=item,
        account=account,
        order=order,
        line=line,
    )


def test_migration_roundtrip_schema_and_no_model_drift(databases):
    database, runtime, migrate = databases
    assert set(inspect(database.engine).get_table_names()) == set(
        Base.metadata.tables
    ) | {"alembic_version"}
    migrate("check")
    with runtime.sessions() as session:
        assert check_database(session)["status"] == "ready"
        assert (
            session.execute(text("SELECT current_user")).scalar_one()
            == "dailydabba_app"
        )


def test_exact_prices_and_historical_snapshots(session, records):
    line = records["line"]
    assert line.line_total_paise == 10000
    records["item"].price_paise = 9999
    session.flush()
    session.refresh(line)
    assert (line.unit_price_paise, line.line_total_paise) == (5000, 10000)
    with pytest.raises(IntegrityError), session.begin_nested():
        records["food"].price_paise = -1
        session.flush()


def test_order_rejects_another_users_address(session, records):
    with pytest.raises(IntegrityError), session.begin_nested():
        records["order"].address_id = records["other_address"].id
        session.flush()


def test_only_one_live_default_address(session, records):
    address = records["address"]
    with pytest.raises(IntegrityError), session.begin_nested():
        session.add(
            models.Address(
                user_id=address.user_id,
                label="duplicate",
                recipient_name="test",
                phone="0000000000",
                line1="test",
                locality="test",
                city="Chennai",
                state="Tamil Nadu",
                postal_code="600003",
                is_default=True,
            )
        )
        session.flush()


def test_nonnegative_credit_balance_and_duplicate_purchase_grant(session, records):
    account = records["account"]
    with pytest.raises(IntegrityError), session.begin_nested():
        account.balance = -1
        session.flush()
    with pytest.raises(IntegrityError), session.begin_nested():
        session.add(
            models.CreditTransaction(
                account_id=account.id,
                user_id=records["user"].id,
                kind="grant",
                delta=5,
                event_key="changed-retry-key",
                request_hash="d" * 64,
                reason="duplicate purchase",
            )
        )
        session.flush()


def test_duplicate_order_idempotency_and_totals_rejected(session, records):
    with pytest.raises(IntegrityError), session.begin_nested():
        records["order"].total_paise = 1
        session.flush()
    with pytest.raises(IntegrityError), session.begin_nested():
        records["order"].delivery_end_at = datetime(
            2026, 11, 13, 7, 30, tzinfo=timezone.utc
        )
        session.flush()
    values = {
        c.name: getattr(records["order"], c.name)
        for c in models.Order.__table__.columns
        if c.name not in {"id", "created_at"}
    }
    with pytest.raises(IntegrityError), session.begin_nested():
        session.add(models.Order(**values))
        session.flush()


def test_order_history_cannot_be_deleted_with_items(session, records):
    with pytest.raises(IntegrityError), session.begin_nested():
        session.execute(
            delete(models.Order).where(models.Order.id == records["order"].id)
        )


@pytest.mark.parametrize(
    "statement",
    [
        "CREATE TABLE public.runtime_must_not_create (id int)",
        "UPDATE public.orders SET subtotal_paise = 0 WHERE false",
        "DELETE FROM public.credit_transactions WHERE false",
        "UPDATE public.audit_logs SET action = 'changed' WHERE false",
        "DELETE FROM public.alembic_version WHERE false",
    ],
)
def test_runtime_role_cannot_change_schema_or_immutable_history(databases, statement):
    _, runtime, _ = databases
    with pytest.raises(DBAPIError) as error:
        with runtime.engine.begin() as connection:
            connection.execute(text(statement))
    assert error.value.orig.sqlstate == "42501"


def test_request_sessions_rollback_uncommitted_work_and_readiness_is_live(databases):
    _, runtime, _ = databases
    url = SecretStr(runtime.engine.url.render_as_string(hide_password=False))
    application = create_app(Settings(_env_file=None, database_url=url))
    unique_name = "rollback-" + str(uuid4())

    @application.post("/test-rollback")
    def write_then_fail(session: DbSession):
        session.add(models.FoodCategory(name=unique_name))
        session.flush()
        raise HTTPException(409, "Deliberate test rollback")

    with TestClient(application) as client:
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/api/v1/ready").json() == {"status": "ready"}
        assert client.post("/test-rollback").status_code == 409
    with runtime.sessions() as session:
        assert (
            session.execute(
                text("SELECT count(*) FROM food_categories WHERE name = :name"),
                {"name": unique_name},
            ).scalar_one()
            == 0
        )


def test_payment_targets_provider_uniqueness_and_refund_amounts(session, records):
    payment = models.Payment(
        user_id=records["user"].id,
        order_id=records["order"].id,
        amount_paise=10000,
        provider_payment_id="test-provider-id",
        idempotency_key="attempt-one",
        request_hash="e" * 64,
    )
    session.add(payment)
    session.flush()
    with pytest.raises(IntegrityError), session.begin_nested():
        payment.subscription_id = records["subscription"].id
        session.flush()
    with pytest.raises(IntegrityError), session.begin_nested():
        session.add(
            models.Payment(
                user_id=records["user"].id,
                order_id=records["order"].id,
                amount_paise=10000,
                provider_payment_id="test-provider-id",
                idempotency_key="different-request",
                request_hash="f" * 64,
            )
        )
        session.flush()
    with pytest.raises(IntegrityError), session.begin_nested():
        session.add(
            models.Refund(
                payment_id=payment.id,
                amount_paise=-1,
                reason="invalid amount",
                idempotency_key="refund-one",
                request_hash="a" * 64,
            )
        )
        session.flush()
```

### app/tests/test_database_unit.py

```python
"""Configuration secrecy and liveness behavior without a configured database."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.main import create_app


def test_database_secrets_are_not_in_settings_representation():
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://app:private_password@localhost/db",
    )
    assert "private_password" not in repr(settings)
    assert "private_password" not in settings.model_dump_json()


def test_invalid_database_url_does_not_expose_input():
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None, database_url="sqlite://secret_password")
    assert "secret_password" not in str(error.value)


def test_liveness_is_independent_of_database_configuration():
    with TestClient(create_app(Settings(_env_file=None))) as client:
        assert client.get("/api/v1/health").json() == {"status": "ok"}
        response = client.get("/api/v1/ready")
        assert response.status_code == 503
        assert response.json() == {"detail": "Database unavailable"}


def test_readiness_database_errors_are_sanitized():
    from unittest.mock import Mock
    from sqlalchemy.exc import SQLAlchemyError
    from app.db.database import get_session

    fake_session = Mock()
    fake_session.execute.side_effect = SQLAlchemyError(
        "private_password must not appear"
    )
    application = create_app(Settings(_env_file=None))
    application.dependency_overrides[get_session] = lambda: fake_session
    with TestClient(application) as client:
        response = client.get("/api/v1/ready")
        assert response.status_code == 503
        assert response.json() == {"detail": "Database unavailable"}
        assert "private_password" not in response.text
```

### app/tests/test_health.py

```python
"""Verify the Phase 1 HTTP contract and automatic API documentation."""

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def client():
    """Run startup/shutdown as the real server would, without external services."""
    with TestClient(create_app(Settings(_env_file=None))) as test_client:
        yield test_client


def test_health_returns_expected_public_contract(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_documents_health_response(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    operation = response.json()["paths"]["/api/v1/health"]["get"]
    schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema["$ref"] == "#/components/schemas/HealthResponse"


def test_swagger_documentation_is_served(client: TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text


def test_unknown_endpoint_returns_404(client: TestClient) -> None:
    assert client.get("/api/v1/unknown").status_code == 404
```

### app/tests/test_models.py

```python
"""Check model wiring and PostgreSQL DDL, without claiming database integration."""

from sqlalchemy import DateTime, Float, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.orm import configure_mappers
from sqlalchemy.schema import CreateIndex

import app.models  # noqa: F401
from app.db.base import Base
from app.db.export_schema import render_schema
from app.models.commerce import Order, OrderItem
from app.models.identity import Address
from app.models.subscriptions import CreditTransaction


def test_all_mappings_and_foreign_keys_resolve() -> None:
    configure_mappers()
    assert len(Base.metadata.tables) == 23
    for table in Base.metadata.sorted_tables:
        for foreign_key in table.foreign_keys:
            assert foreign_key.column.table in Base.metadata.tables.values()


def test_schema_compiles_for_postgresql_without_a_driver() -> None:
    ddl = render_schema()
    assert ddl.count("CREATE TABLE ") == 23
    assert "TIMESTAMP WITH TIME ZONE" in ddl
    assert "JSONB" in ddl
    assert "GENERATED ALWAYS AS (unit_price_paise * quantity) STORED" in ddl
    assert "AT TIME ZONE 'Asia/Kolkata'" in ddl


def test_all_money_is_exact_and_all_event_timestamps_are_timezone_aware() -> None:
    for table in Base.metadata.tables.values():
        for column in table.columns:
            assert not isinstance(column.type, Float)
            if isinstance(column.type, DateTime):
                assert column.type.timezone
            if column.name.endswith("_paise"):
                assert column.type.python_type is int


def test_owned_order_address_uses_one_composite_foreign_key() -> None:
    constraints = [
        c for c in Order.__table__.constraints if isinstance(c, ForeignKeyConstraint)
    ]
    ownership = next(
        c for c in constraints if set(c.column_keys) == {"address_id", "user_id"}
    )
    assert [element.target_fullname for element in ownership.elements] == [
        "addresses.id",
        "addresses.user_id",
    ]


def test_default_address_uniqueness_only_applies_to_live_defaults() -> None:
    index = next(
        i
        for i in Address.__table__.indexes
        if i.name == "uq_addresses_one_live_default"
    )
    ddl = str(CreateIndex(index).compile(dialect=dialect()))
    assert "UNIQUE INDEX" in ddl
    assert "WHERE is_default AND deleted_at IS NULL" in ddl


def test_financial_history_has_no_cascading_delete() -> None:
    for table in Base.metadata.tables.values():
        for foreign_key in table.foreign_keys:
            if foreign_key.ondelete == "CASCADE":
                assert table.name == "cart_items"
    assert OrderItem.__table__.c.line_total_paise.computed is not None


def test_credit_retry_and_business_event_both_have_unique_keys() -> None:
    keys = {
        tuple(c.columns.keys())
        for c in CreditTransaction.__table__.constraints
        if isinstance(c, UniqueConstraint)
    }
    assert ("account_id", "event_key") in keys
    assert ("account_id", "order_id", "kind") in keys


def test_renewal_owner_and_purchase_grant_guards_compile() -> None:
    subscription = Base.metadata.tables["subscriptions"]
    constraints = [
        c for c in subscription.constraints if isinstance(c, ForeignKeyConstraint)
    ]
    renewal = next(
        c for c in constraints if set(c.column_keys) == {"renewed_from_id", "user_id"}
    )
    assert [e.target_fullname for e in renewal.elements] == [
        "subscriptions.id",
        "subscriptions.user_id",
    ]
    index = next(
        i
        for i in CreditTransaction.__table__.indexes
        if i.name == "uq_credit_account_purchase_grant"
    )
    ddl = str(CreateIndex(index).compile(dialect=dialect()))
    assert "UNIQUE INDEX" in ddl
    assert "WHERE kind = 'grant'" in ddl
```

### app/tests/test_security.py

```python
"""Password, JWT, configuration and bounded rate-limiter behavior without a DB."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError

from app.core.config import Settings
from app.core.rate_limit import AuthRateLimiter
from app.core.security import (
    AuthNotConfigured,
    InvalidCredentials,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.db.database import get_session
from app.main import create_app


@pytest.fixture
def settings():
    return Settings(
        _env_file=None,
        jwt_secret=SecretStr("unit-test-signing-key-with-at-least-32-bytes"),
    )


def claims(settings):
    now = datetime.now(timezone.utc)
    return {
        "sub": str(uuid4()),
        "jti": str(uuid4()),
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=15),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "token_type": "access",
    }


def test_argon2_is_salted_and_verification_fails_closed():
    password = "test-only long password"
    one, two = hash_password(password), hash_password(password)
    assert one.startswith("$argon2id$") and one != two
    assert password not in one
    assert verify_password(password, one)[0]
    assert not verify_password("wrong password", one)[0]
    assert not verify_password(password, None)[0]
    assert not verify_password(password, "invalid hash")[0]
    assert not verify_password(password, "$argon2id$invalid")[0]


def test_signed_access_token_roundtrip(settings):
    subject = uuid4()
    token = create_access_token(subject, settings)
    assert decode_access_token(token, settings) == subject


@pytest.mark.parametrize(
    "fault",
    [
        "expired",
        "missing_exp",
        "missing_iat",
        "missing_nbf",
        "missing_jti",
        "missing_sub",
        "wrong_issuer",
        "wrong_audience",
        "wrong_key",
        "wrong_algorithm",
        "wrong_type",
        "invalid_sub",
        "invalid_jti",
        "future_nbf",
        "future_iat",
        "unsigned",
    ],
)
def test_jwt_invalid_claims_or_signatures_are_rejected(settings, fault):
    payload = claims(settings)
    key = settings.jwt_secret.get_secret_value()
    algorithm = "HS256"
    if fault == "expired":
        payload["exp"] = datetime.now(timezone.utc) - timedelta(seconds=10)
    elif fault.startswith("missing_"):
        del payload[fault.removeprefix("missing_")]
    elif fault == "wrong_issuer":
        payload["iss"] = "another-api"
    elif fault == "wrong_audience":
        payload["aud"] = "another-client"
    elif fault == "wrong_key":
        key = "another-signing-key-with-at-least-32-bytes"
    elif fault == "wrong_algorithm":
        algorithm = "HS384"
        key = key * 2
    elif fault == "wrong_type":
        payload["token_type"] = "refresh"
    elif fault == "invalid_sub":
        payload["sub"] = "not-a-uuid"
    elif fault == "invalid_jti":
        payload["jti"] = "not-a-uuid"
    elif fault == "future_nbf":
        payload["nbf"] = datetime.now(timezone.utc) + timedelta(minutes=5)
    elif fault == "future_iat":
        payload["iat"] = datetime.now(timezone.utc) + timedelta(minutes=5)
    elif fault == "unsigned":
        algorithm, key = "none", ""
    token = jwt.encode(payload, key, algorithm=algorithm)
    with pytest.raises(InvalidCredentials):
        decode_access_token(token, settings)


def test_missing_key_disables_auth_without_guessing_defaults():
    with pytest.raises(AuthNotConfigured):
        create_access_token(uuid4(), Settings(_env_file=None))
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None, jwt_secret="too-short-secret")
    assert "too-short-secret" not in str(error.value)


def test_rate_limit_is_atomic_and_expires():
    clock = [0.0]
    limiter = AuthRateLimiter(2, clock=lambda: clock[0])
    with ThreadPoolExecutor(max_workers=8) as pool:
        outcomes = list(
            pool.map(lambda _: limiter.retry_after("same-client"), range(20))
        )
    assert outcomes.count(None) == 2
    assert limiter.retry_after("another-client") is None
    clock[0] = 60.1
    assert limiter.retry_after("same-client") is None


def test_rate_limiter_storage_is_bounded():
    limiter = AuthRateLimiter(1, clock=lambda: 0)
    for index in range(4096):
        assert limiter.retry_after(str(index)) is None
    assert limiter.retry_after("new-client") == 60


def test_validation_does_not_echo_passwords_and_auth_is_throttled(settings):
    settings.auth_rate_limit_per_minute = 2
    application = create_app(settings)
    application.dependency_overrides[get_session] = lambda: object()
    with TestClient(application) as client:
        for _ in range(2):
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "p4X!q",
                    "full_name": "Test",
                },
            )
            assert response.status_code == 422
            assert "p4X!q" not in response.text
            assert "input" not in response.text
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "p4X!q",
                "full_name": "Test",
            },
        )
        assert response.status_code == 429
        assert int(response.headers["retry-after"]) > 0
        assert response.headers["cache-control"] == "no-store"


def test_missing_or_invalid_bearer_token_is_401_without_database(settings):
    with TestClient(create_app(settings)) as client:
        for headers in [
            {},
            {"Authorization": "Bearer invalid"},
            {"Authorization": "Basic invalid"},
        ]:
            response = client.get("/api/v1/users/me", headers=headers)
            assert response.status_code == 401
            assert response.headers["www-authenticate"] == "Bearer"
```

### alembic/env.py

```python
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
```

### alembic/versions/0001_initial_initial_database_schema.py

```python
"""initial database schema

Revision ID: 0001_initial
Revises: none
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Reviewed initial schema and explicit runtime grants.
    op.create_table(
        "daily_menus",
        sa.Column("business_date", sa.Date(), nullable=False),
        sa.Column("meal_type", sa.String(length=12), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "meal_type IN ('breakfast', 'lunch', 'dinner')",
            name=op.f("ck_daily_menus_meal_type"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_daily_menus")),
        sa.UniqueConstraint(
            "business_date",
            "meal_type",
            name=op.f("uq_daily_menus_business_date_meal_type"),
        ),
        sa.UniqueConstraint(
            "id",
            "business_date",
            "meal_type",
            name=op.f("uq_daily_menus_id_business_date_meal_type"),
        ),
    )
    op.create_table(
        "delivery_slots",
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("meal_type", sa.String(length=12), nullable=False),
        sa.Column("start_local", sa.Time(), nullable=False),
        sa.Column("end_local", sa.Time(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "meal_type IN ('breakfast', 'lunch', 'dinner')",
            name=op.f("ck_delivery_slots_meal_type"),
        ),
        sa.CheckConstraint(
            "end_local > start_local", name=op.f("ck_delivery_slots_time_window")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_delivery_slots")),
        sa.UniqueConstraint(
            "id", "meal_type", name=op.f("uq_delivery_slots_id_meal_type")
        ),
        sa.UniqueConstraint(
            "meal_type",
            "start_local",
            "end_local",
            name=op.f("uq_delivery_slots_meal_type_start_local_end_local"),
        ),
    )
    op.create_table(
        "food_categories",
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_food_categories")),
        sa.UniqueConstraint("name", name=op.f("uq_food_categories_name")),
    )
    op.create_table(
        "subscription_plans",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("period", sa.String(length=12), nullable=False),
        sa.Column("meal_type", sa.String(length=12), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("included_credits", sa.Integer(), nullable=False),
        sa.Column("price_paise", sa.BigInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "meal_type IN ('breakfast', 'lunch', 'dinner')",
            name=op.f("ck_subscription_plans_meal_type"),
        ),
        sa.CheckConstraint(
            "period IN ('weekly', 'monthly')", name=op.f("ck_subscription_plans_period")
        ),
        sa.CheckConstraint(
            "duration_days > 0 AND included_credits > 0 AND price_paise >= 0",
            name=op.f("ck_subscription_plans_terms_positive"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscription_plans")),
        sa.UniqueConstraint("code", name=op.f("uq_subscription_plans_code")),
    )
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "role IN ('customer', 'admin', 'kitchen_staff')", name=op.f("ck_users_role")
        ),
        sa.CheckConstraint(
            "email = lower(email) AND length(email) > 3",
            name=op.f("ck_users_email_normalized"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_table(
        "addresses",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("label", sa.String(length=50), nullable=False),
        sa.Column("recipient_name", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("line1", sa.String(length=200), nullable=False),
        sa.Column("line2", sa.String(length=200), nullable=True),
        sa.Column("locality", sa.String(length=120), nullable=False),
        sa.Column("city", sa.String(length=80), nullable=False),
        sa.Column("state", sa.String(length=80), nullable=False),
        sa.Column("postal_code", sa.String(length=6), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "NOT is_default OR deleted_at IS NULL",
            name=op.f("ck_addresses_default_not_deleted"),
        ),
        sa.CheckConstraint(
            "length(postal_code) = 6", name=op.f("ck_addresses_postal_code_length")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_addresses_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_addresses")),
        sa.UniqueConstraint("id", "user_id", name=op.f("uq_addresses_id_user_id")),
    )
    op.create_index(
        op.f("ix_addresses_user_id"), "addresses", ["user_id"], unique=False
    )
    op.create_index(
        "uq_addresses_one_live_default",
        "addresses",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("is_default AND deleted_at IS NULL"),
    )
    op.create_table(
        "audit_logs",
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "jsonb_typeof(details) = 'object'",
            name=op.f("ck_audit_logs_details_object"),
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name=op.f("fk_audit_logs_actor_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
    )
    op.create_index(
        op.f("ix_audit_logs_actor_user_id"),
        "audit_logs",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_audit_logs_target_id"), "audit_logs", ["target_id"], unique=False
    )
    op.create_table(
        "carts",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("menu_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["menu_id"],
            ["daily_menus.id"],
            name=op.f("fk_carts_menu_id_daily_menus"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_carts_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_carts")),
        sa.UniqueConstraint("id", "menu_id", name=op.f("uq_carts_id_menu_id")),
        sa.UniqueConstraint("user_id", name=op.f("uq_carts_user_id")),
    )
    op.create_index(op.f("ix_carts_menu_id"), "carts", ["menu_id"], unique=False)
    op.create_table(
        "customer_profiles",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_customer_profiles_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_customer_profiles")),
        sa.UniqueConstraint("user_id", name=op.f("uq_customer_profiles_user_id")),
    )
    op.create_table(
        "food_items",
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("price_paise", sa.BigInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "price_paise >= 0", name=op.f("ck_food_items_price_nonnegative")
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["food_categories.id"],
            name=op.f("fk_food_items_category_id_food_categories"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_food_items")),
    )
    op.create_index(
        op.f("ix_food_items_category_id"), "food_items", ["category_id"], unique=False
    )
    op.create_table(
        "notifications",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("event_key", sa.String(length=150), nullable=False),
        sa.Column("channel", sa.String(length=12), nullable=False),
        sa.Column("status", sa.String(length=12), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "channel IN ('in_app', 'email', 'sms')",
            name=op.f("ck_notifications_channel"),
        ),
        sa.CheckConstraint(
            "jsonb_typeof(payload) = 'object'",
            name=op.f("ck_notifications_payload_object"),
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'sent', 'failed', 'read')",
            name=op.f("ck_notifications_status"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_notifications_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notifications")),
        sa.UniqueConstraint("event_key", name=op.f("uq_notifications_event_key")),
    )
    op.create_index(
        op.f("ix_notifications_status"), "notifications", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False
    )
    op.create_table(
        "subscriptions",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.Column("renewed_from_id", sa.Uuid(), nullable=True),
        sa.Column("plan_name", sa.String(length=120), nullable=False),
        sa.Column("meal_type", sa.String(length=12), nullable=False),
        sa.Column("purchased_credits", sa.Integer(), nullable=False),
        sa.Column("price_paise", sa.BigInteger(), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("expires_on", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "policy_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "jsonb_typeof(policy_snapshot) = 'object'",
            name=op.f("ck_subscriptions_policy_object"),
        ),
        sa.CheckConstraint(
            "meal_type IN ('breakfast', 'lunch', 'dinner')",
            name=op.f("ck_subscriptions_meal_type"),
        ),
        sa.CheckConstraint(
            "status IN ('pending_payment', 'active', 'paused', 'expired', 'cancelled')",
            name=op.f("ck_subscriptions_status"),
        ),
        sa.CheckConstraint(
            "expires_on > starts_on", name=op.f("ck_subscriptions_date_window")
        ),
        sa.CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name=op.f("ck_subscriptions_request_identity"),
        ),
        sa.CheckConstraint(
            "purchased_credits > 0 AND price_paise >= 0",
            name=op.f("ck_subscriptions_purchased_terms"),
        ),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["subscription_plans.id"],
            name=op.f("fk_subscriptions_plan_id_subscription_plans"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["renewed_from_id", "user_id"],
            ["subscriptions.id", "subscriptions.user_id"],
            name=op.f("fk_subscriptions_renewed_from_id_user_id_subscriptions"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_subscriptions_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscriptions")),
        sa.UniqueConstraint("id", "user_id", name=op.f("uq_subscriptions_id_user_id")),
        sa.UniqueConstraint(
            "user_id",
            "idempotency_key",
            name=op.f("uq_subscriptions_user_id_idempotency_key"),
        ),
    )
    op.create_index(
        op.f("ix_subscriptions_plan_id"), "subscriptions", ["plan_id"], unique=False
    )
    op.create_index(
        op.f("ix_subscriptions_renewed_from_id"),
        "subscriptions",
        ["renewed_from_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscriptions_status"), "subscriptions", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_subscriptions_user_id"), "subscriptions", ["user_id"], unique=False
    )
    op.create_table(
        "menu_items",
        sa.Column("menu_id", sa.Uuid(), nullable=False),
        sa.Column("food_item_id", sa.Uuid(), nullable=False),
        sa.Column("price_paise", sa.BigInteger(), nullable=False),
        sa.Column("portions_remaining", sa.Integer(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "portions_remaining >= 0", name=op.f("ck_menu_items_stock_nonnegative")
        ),
        sa.CheckConstraint(
            "price_paise >= 0", name=op.f("ck_menu_items_price_nonnegative")
        ),
        sa.ForeignKeyConstraint(
            ["food_item_id"],
            ["food_items.id"],
            name=op.f("fk_menu_items_food_item_id_food_items"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["menu_id"],
            ["daily_menus.id"],
            name=op.f("fk_menu_items_menu_id_daily_menus"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_menu_items")),
        sa.UniqueConstraint("id", "menu_id", name=op.f("uq_menu_items_id_menu_id")),
        sa.UniqueConstraint(
            "menu_id", "food_item_id", name=op.f("uq_menu_items_menu_id_food_item_id")
        ),
    )
    op.create_index(
        op.f("ix_menu_items_food_item_id"), "menu_items", ["food_item_id"], unique=False
    )
    op.create_index(
        op.f("ix_menu_items_menu_id"), "menu_items", ["menu_id"], unique=False
    )
    op.create_table(
        "orders",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("address_id", sa.Uuid(), nullable=False),
        sa.Column(
            "address_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("menu_id", sa.Uuid(), nullable=False),
        sa.Column("business_date", sa.Date(), nullable=False),
        sa.Column("meal_type", sa.String(length=12), nullable=False),
        sa.Column("delivery_slot_id", sa.Uuid(), nullable=False),
        sa.Column("delivery_start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivery_end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("subtotal_paise", sa.BigInteger(), nullable=False),
        sa.Column("delivery_fee_paise", sa.BigInteger(), nullable=False),
        sa.Column("tax_paise", sa.BigInteger(), nullable=False),
        sa.Column("discount_paise", sa.BigInteger(), nullable=False),
        sa.Column("total_paise", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "business_date = (delivery_start_at AT TIME ZONE 'Asia/Kolkata')::date AND business_date = (delivery_end_at AT TIME ZONE 'Asia/Kolkata')::date",
            name=op.f("ck_orders_business_date_local"),
        ),
        sa.CheckConstraint(
            "jsonb_typeof(address_snapshot) = 'object'",
            name=op.f("ck_orders_address_object"),
        ),
        sa.CheckConstraint(
            "status IN ('pending_payment', 'placed', 'confirmed', 'preparing', 'ready', 'out_for_delivery', 'delivered', 'cancelled')",
            name=op.f("ck_orders_status"),
        ),
        sa.CheckConstraint(
            "delivery_end_at > delivery_start_at",
            name=op.f("ck_orders_delivery_window"),
        ),
        sa.CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name=op.f("ck_orders_request_identity"),
        ),
        sa.CheckConstraint(
            "subtotal_paise >= 0 AND delivery_fee_paise >= 0 AND tax_paise >= 0 AND discount_paise >= 0 AND total_paise >= 0",
            name=op.f("ck_orders_amounts_nonnegative"),
        ),
        sa.CheckConstraint(
            "total_paise = subtotal_paise + delivery_fee_paise + tax_paise - discount_paise",
            name=op.f("ck_orders_total_equation"),
        ),
        sa.ForeignKeyConstraint(
            ["address_id", "user_id"],
            ["addresses.id", "addresses.user_id"],
            name=op.f("fk_orders_address_id_user_id_addresses"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["delivery_slot_id", "meal_type"],
            ["delivery_slots.id", "delivery_slots.meal_type"],
            name=op.f("fk_orders_delivery_slot_id_meal_type_delivery_slots"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["menu_id", "business_date", "meal_type"],
            ["daily_menus.id", "daily_menus.business_date", "daily_menus.meal_type"],
            name=op.f("fk_orders_menu_id_business_date_meal_type_daily_menus"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_orders_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orders")),
        sa.UniqueConstraint("id", "menu_id", name=op.f("uq_orders_id_menu_id")),
        sa.UniqueConstraint("id", "user_id", name=op.f("uq_orders_id_user_id")),
        sa.UniqueConstraint(
            "user_id", "idempotency_key", name=op.f("uq_orders_user_id_idempotency_key")
        ),
    )
    op.create_index(
        op.f("ix_orders_address_id"), "orders", ["address_id"], unique=False
    )
    op.create_index(
        op.f("ix_orders_business_date"), "orders", ["business_date"], unique=False
    )
    op.create_index(
        op.f("ix_orders_delivery_slot_id"), "orders", ["delivery_slot_id"], unique=False
    )
    op.create_index(op.f("ix_orders_menu_id"), "orders", ["menu_id"], unique=False)
    op.create_index(op.f("ix_orders_status"), "orders", ["status"], unique=False)
    op.create_index(op.f("ix_orders_user_id"), "orders", ["user_id"], unique=False)
    op.create_table(
        "subscription_credits",
        sa.Column("subscription_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("balance", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "balance >= 0", name=op.f("ck_subscription_credits_balance_nonnegative")
        ),
        sa.ForeignKeyConstraint(
            ["subscription_id", "user_id"],
            ["subscriptions.id", "subscriptions.user_id"],
            name=op.f("fk_subscription_credits_subscription_id_user_id_subscriptions"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscription_credits")),
        sa.UniqueConstraint(
            "id", "user_id", name=op.f("uq_subscription_credits_id_user_id")
        ),
        sa.UniqueConstraint(
            "subscription_id", name=op.f("uq_subscription_credits_subscription_id")
        ),
    )
    op.create_index(
        op.f("ix_subscription_credits_user_id"),
        "subscription_credits",
        ["user_id"],
        unique=False,
    )
    op.create_table(
        "subscription_events",
        sa.Column("subscription_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=16), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("event_key", sa.String(length=128), nullable=False),
        sa.Column("reason", sa.String(length=300), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "event_type IN ('activate', 'pause', 'resume', 'skip', 'renew', 'expire', 'cancel')",
            name=op.f("ck_subscription_events_event_type"),
        ),
        sa.CheckConstraint(
            "length(event_key) > 0", name=op.f("ck_subscription_events_event_key")
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name=op.f("fk_subscription_events_actor_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["subscription_id"],
            ["subscriptions.id"],
            name=op.f("fk_subscription_events_subscription_id_subscriptions"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscription_events")),
        sa.UniqueConstraint(
            "subscription_id",
            "event_key",
            name=op.f("uq_subscription_events_subscription_id_event_key"),
        ),
    )
    op.create_index(
        op.f("ix_subscription_events_actor_user_id"),
        "subscription_events",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscription_events_subscription_id"),
        "subscription_events",
        ["subscription_id"],
        unique=False,
    )
    op.create_index(
        "uq_subscription_skip_date",
        "subscription_events",
        ["subscription_id", "effective_date"],
        unique=True,
        postgresql_where=sa.text("event_type = 'skip'"),
    )
    op.create_table(
        "cart_items",
        sa.Column("cart_id", sa.Uuid(), nullable=False),
        sa.Column("menu_id", sa.Uuid(), nullable=False),
        sa.Column("menu_item_id", sa.Uuid(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantity > 0", name=op.f("ck_cart_items_quantity_positive")
        ),
        sa.ForeignKeyConstraint(
            ["cart_id", "menu_id"],
            ["carts.id", "carts.menu_id"],
            name=op.f("fk_cart_items_cart_id_menu_id_carts"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["menu_item_id", "menu_id"],
            ["menu_items.id", "menu_items.menu_id"],
            name=op.f("fk_cart_items_menu_item_id_menu_id_menu_items"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cart_items")),
        sa.UniqueConstraint(
            "cart_id", "menu_item_id", name=op.f("uq_cart_items_cart_id_menu_item_id")
        ),
    )
    op.create_index(
        op.f("ix_cart_items_cart_id"), "cart_items", ["cart_id"], unique=False
    )
    op.create_index(
        op.f("ix_cart_items_menu_id"), "cart_items", ["menu_id"], unique=False
    )
    op.create_index(
        op.f("ix_cart_items_menu_item_id"), "cart_items", ["menu_item_id"], unique=False
    )
    op.create_table(
        "credit_transactions",
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=True),
        sa.Column("kind", sa.String(length=12), nullable=False),
        sa.Column("delta", sa.Integer(), nullable=False),
        sa.Column("event_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("reason", sa.String(length=300), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(kind IN ('grant', 'restore') AND delta > 0) OR (kind IN ('debit', 'expire') AND delta < 0) OR kind = 'adjust'",
            name=op.f("ck_credit_transactions_delta_direction"),
        ),
        sa.CheckConstraint(
            "kind IN ('grant', 'debit', 'restore', 'expire', 'adjust')",
            name=op.f("ck_credit_transactions_kind"),
        ),
        sa.CheckConstraint(
            "kind NOT IN ('debit', 'restore') OR order_id IS NOT NULL",
            name=op.f("ck_credit_transactions_order_required"),
        ),
        sa.CheckConstraint(
            "delta <> 0", name=op.f("ck_credit_transactions_delta_nonzero")
        ),
        sa.CheckConstraint(
            "length(event_key) > 0 AND length(request_hash) = 64 AND length(reason) > 0",
            name=op.f("ck_credit_transactions_event_identity"),
        ),
        sa.ForeignKeyConstraint(
            ["account_id", "user_id"],
            ["subscription_credits.id", "subscription_credits.user_id"],
            name=op.f("fk_credit_transactions_account_id_user_id_subscription_credits"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name=op.f("fk_credit_transactions_actor_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["order_id", "user_id"],
            ["orders.id", "orders.user_id"],
            name=op.f("fk_credit_transactions_order_id_user_id_orders"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_credit_transactions")),
        sa.UniqueConstraint(
            "account_id",
            "event_key",
            name=op.f("uq_credit_transactions_account_id_event_key"),
        ),
        sa.UniqueConstraint(
            "account_id",
            "order_id",
            "kind",
            name=op.f("uq_credit_transactions_account_id_order_id_kind"),
        ),
    )
    op.create_index(
        op.f("ix_credit_transactions_account_id"),
        "credit_transactions",
        ["account_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_credit_transactions_actor_user_id"),
        "credit_transactions",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_credit_transactions_order_id"),
        "credit_transactions",
        ["order_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_credit_transactions_user_id"),
        "credit_transactions",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "uq_credit_account_purchase_grant",
        "credit_transactions",
        ["account_id"],
        unique=True,
        postgresql_where=sa.text("kind = 'grant'"),
    )
    op.create_table(
        "kitchen_orders",
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ready_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'preparing', 'ready', 'completed', 'cancelled')",
            name=op.f("ck_kitchen_orders_status"),
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            name=op.f("fk_kitchen_orders_order_id_orders"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_kitchen_orders")),
        sa.UniqueConstraint("order_id", name=op.f("uq_kitchen_orders_order_id")),
    )
    op.create_index(
        op.f("ix_kitchen_orders_status"), "kitchen_orders", ["status"], unique=False
    )
    op.create_table(
        "order_items",
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("menu_id", sa.Uuid(), nullable=False),
        sa.Column("menu_item_id", sa.Uuid(), nullable=False),
        sa.Column("food_name", sa.String(length=120), nullable=False),
        sa.Column("unit_price_paise", sa.BigInteger(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column(
            "line_total_paise",
            sa.BigInteger(),
            sa.Computed("unit_price_paise * quantity", persisted=True),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantity > 0 AND unit_price_paise >= 0",
            name=op.f("ck_order_items_item_amount"),
        ),
        sa.ForeignKeyConstraint(
            ["menu_item_id", "menu_id"],
            ["menu_items.id", "menu_items.menu_id"],
            name=op.f("fk_order_items_menu_item_id_menu_id_menu_items"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["order_id", "menu_id"],
            ["orders.id", "orders.menu_id"],
            name=op.f("fk_order_items_order_id_menu_id_orders"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_items")),
        sa.UniqueConstraint(
            "order_id",
            "menu_item_id",
            name=op.f("uq_order_items_order_id_menu_item_id"),
        ),
    )
    op.create_index(
        op.f("ix_order_items_menu_id"), "order_items", ["menu_id"], unique=False
    )
    op.create_index(
        op.f("ix_order_items_menu_item_id"),
        "order_items",
        ["menu_item_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_order_items_order_id"), "order_items", ["order_id"], unique=False
    )
    op.create_table(
        "payments",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=True),
        sa.Column("subscription_id", sa.Uuid(), nullable=True),
        sa.Column("amount_paise", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("provider_order_id", sa.String(length=100), nullable=True),
        sa.Column("provider_payment_id", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(status = 'captured') = (captured_at IS NOT NULL)",
            name=op.f("ck_payments_capture_instant"),
        ),
        sa.CheckConstraint(
            "amount_paise > 0 AND currency = 'INR'",
            name=op.f("ck_payments_amount_currency"),
        ),
        sa.CheckConstraint("provider = 'razorpay'", name=op.f("ck_payments_provider")),
        sa.CheckConstraint(
            "status IN ('created', 'authorized', 'captured', 'failed')",
            name=op.f("ck_payments_status"),
        ),
        sa.CheckConstraint(
            "(order_id IS NOT NULL AND subscription_id IS NULL) OR (order_id IS NULL AND subscription_id IS NOT NULL)",
            name=op.f("ck_payments_one_target"),
        ),
        sa.CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name=op.f("ck_payments_request_identity"),
        ),
        sa.ForeignKeyConstraint(
            ["order_id", "user_id"],
            ["orders.id", "orders.user_id"],
            name=op.f("fk_payments_order_id_user_id_orders"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["subscription_id", "user_id"],
            ["subscriptions.id", "subscriptions.user_id"],
            name=op.f("fk_payments_subscription_id_user_id_subscriptions"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_payments_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_payments")),
        sa.UniqueConstraint(
            "provider",
            "provider_payment_id",
            name=op.f("uq_payments_provider_provider_payment_id"),
        ),
        sa.UniqueConstraint(
            "user_id",
            "idempotency_key",
            name=op.f("uq_payments_user_id_idempotency_key"),
        ),
    )
    op.create_index(
        op.f("ix_payments_order_id"), "payments", ["order_id"], unique=False
    )
    op.create_index(
        op.f("ix_payments_provider_order_id"),
        "payments",
        ["provider_order_id"],
        unique=False,
    )
    op.create_index(op.f("ix_payments_status"), "payments", ["status"], unique=False)
    op.create_index(
        op.f("ix_payments_subscription_id"),
        "payments",
        ["subscription_id"],
        unique=False,
    )
    op.create_index(op.f("ix_payments_user_id"), "payments", ["user_id"], unique=False)
    op.create_table(
        "payment_webhook_events",
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("provider_event_id", sa.String(length=150), nullable=False),
        sa.Column("payment_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "sanitized_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "jsonb_typeof(sanitized_payload) = 'object'",
            name=op.f("ck_payment_webhook_events_payload_object"),
        ),
        sa.CheckConstraint(
            "provider = 'razorpay'", name=op.f("ck_payment_webhook_events_provider")
        ),
        sa.CheckConstraint(
            "status IN ('received', 'processed', 'failed')",
            name=op.f("ck_payment_webhook_events_status"),
        ),
        sa.CheckConstraint(
            "length(provider_event_id) > 0 AND length(payload_hash) = 64",
            name=op.f("ck_payment_webhook_events_event_identity"),
        ),
        sa.ForeignKeyConstraint(
            ["payment_id"],
            ["payments.id"],
            name=op.f("fk_payment_webhook_events_payment_id_payments"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_payment_webhook_events")),
        sa.UniqueConstraint(
            "provider",
            "provider_event_id",
            name=op.f("uq_payment_webhook_events_provider_provider_event_id"),
        ),
    )
    op.create_index(
        op.f("ix_payment_webhook_events_payment_id"),
        "payment_webhook_events",
        ["payment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_payment_webhook_events_status"),
        "payment_webhook_events",
        ["status"],
        unique=False,
    )
    op.create_table(
        "refunds",
        sa.Column("payment_id", sa.Uuid(), nullable=False),
        sa.Column("amount_paise", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("reason", sa.String(length=300), nullable=False),
        sa.Column("provider_refund_id", sa.String(length=100), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('requested', 'processing', 'succeeded', 'failed')",
            name=op.f("ck_refunds_status"),
        ),
        sa.CheckConstraint("amount_paise > 0", name=op.f("ck_refunds_amount_positive")),
        sa.CheckConstraint(
            "length(idempotency_key) > 0 AND length(request_hash) = 64",
            name=op.f("ck_refunds_request_identity"),
        ),
        sa.ForeignKeyConstraint(
            ["payment_id"],
            ["payments.id"],
            name=op.f("fk_refunds_payment_id_payments"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_refunds")),
        sa.UniqueConstraint(
            "payment_id",
            "idempotency_key",
            name=op.f("uq_refunds_payment_id_idempotency_key"),
        ),
        sa.UniqueConstraint(
            "provider_refund_id", name=op.f("uq_refunds_provider_refund_id")
        ),
    )
    op.create_index(
        op.f("ix_refunds_payment_id"), "refunds", ["payment_id"], unique=False
    )
    # Explicit runtime grants: history/snapshots cannot be updated or deleted.
    op.execute("GRANT SELECT, INSERT ON TABLE public.users TO dailydabba_app")
    op.execute(
        "GRANT SELECT, INSERT ON TABLE public.customer_profiles TO dailydabba_app"
    )
    op.execute("GRANT SELECT, INSERT ON TABLE public.addresses TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.food_categories TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.food_items TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.daily_menus TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.menu_items TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.delivery_slots TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.carts TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.cart_items TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.orders TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.order_items TO dailydabba_app")
    op.execute(
        "GRANT SELECT, INSERT ON TABLE public.subscription_plans TO dailydabba_app"
    )
    op.execute("GRANT SELECT, INSERT ON TABLE public.subscriptions TO dailydabba_app")
    op.execute(
        "GRANT SELECT, INSERT ON TABLE public.subscription_events TO dailydabba_app"
    )
    op.execute(
        "GRANT SELECT, INSERT ON TABLE public.subscription_credits TO dailydabba_app"
    )
    op.execute(
        "GRANT SELECT, INSERT ON TABLE public.credit_transactions TO dailydabba_app"
    )
    op.execute("GRANT SELECT, INSERT ON TABLE public.payments TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.refunds TO dailydabba_app")
    op.execute(
        "GRANT SELECT, INSERT ON TABLE public.payment_webhook_events TO dailydabba_app"
    )
    op.execute("GRANT SELECT, INSERT ON TABLE public.kitchen_orders TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.notifications TO dailydabba_app")
    op.execute("GRANT SELECT, INSERT ON TABLE public.audit_logs TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.users TO dailydabba_app")
    op.execute(
        "GRANT UPDATE, DELETE ON TABLE public.customer_profiles TO dailydabba_app"
    )
    op.execute("GRANT UPDATE, DELETE ON TABLE public.addresses TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.food_categories TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.food_items TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.daily_menus TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.menu_items TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.delivery_slots TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.carts TO dailydabba_app")
    op.execute("GRANT UPDATE, DELETE ON TABLE public.cart_items TO dailydabba_app")
    op.execute(
        "GRANT UPDATE, DELETE ON TABLE public.subscription_plans TO dailydabba_app"
    )
    op.execute("GRANT UPDATE, DELETE ON TABLE public.notifications TO dailydabba_app")
    op.execute("GRANT UPDATE (status) ON TABLE public.orders TO dailydabba_app")
    op.execute(
        "GRANT UPDATE (status, expires_on) ON TABLE public.subscriptions TO dailydabba_app"
    )
    op.execute(
        "GRANT UPDATE (balance) ON TABLE public.subscription_credits TO dailydabba_app"
    )
    op.execute(
        "GRANT UPDATE (status, captured_at, provider_order_id, provider_payment_id) ON TABLE public.payments TO dailydabba_app"
    )
    op.execute(
        "GRANT UPDATE (status, provider_refund_id) ON TABLE public.refunds TO dailydabba_app"
    )
    op.execute(
        "GRANT UPDATE (status, payment_id, processed_at) ON TABLE public.payment_webhook_events TO dailydabba_app"
    )
    op.execute(
        "GRANT UPDATE (status, started_at, ready_at) ON TABLE public.kitchen_orders TO dailydabba_app"
    )
    op.execute("REVOKE ALL ON TABLE public.alembic_version FROM dailydabba_app")
    op.execute("GRANT SELECT ON TABLE public.alembic_version TO dailydabba_app")
    # ### end Alembic commands ###


def downgrade() -> None:
    # Reviewed initial schema and explicit runtime grants.
    op.drop_index(op.f("ix_refunds_payment_id"), table_name="refunds")
    op.drop_table("refunds")
    op.drop_index(
        op.f("ix_payment_webhook_events_status"), table_name="payment_webhook_events"
    )
    op.drop_index(
        op.f("ix_payment_webhook_events_payment_id"),
        table_name="payment_webhook_events",
    )
    op.drop_table("payment_webhook_events")
    op.drop_index(op.f("ix_payments_user_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_subscription_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_status"), table_name="payments")
    op.drop_index(op.f("ix_payments_provider_order_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_order_id"), table_name="payments")
    op.drop_table("payments")
    op.drop_index(op.f("ix_order_items_order_id"), table_name="order_items")
    op.drop_index(op.f("ix_order_items_menu_item_id"), table_name="order_items")
    op.drop_index(op.f("ix_order_items_menu_id"), table_name="order_items")
    op.drop_table("order_items")
    op.drop_index(op.f("ix_kitchen_orders_status"), table_name="kitchen_orders")
    op.drop_table("kitchen_orders")
    op.drop_index(
        "uq_credit_account_purchase_grant",
        table_name="credit_transactions",
        postgresql_where=sa.text("kind = 'grant'"),
    )
    op.drop_index(
        op.f("ix_credit_transactions_user_id"), table_name="credit_transactions"
    )
    op.drop_index(
        op.f("ix_credit_transactions_order_id"), table_name="credit_transactions"
    )
    op.drop_index(
        op.f("ix_credit_transactions_actor_user_id"), table_name="credit_transactions"
    )
    op.drop_index(
        op.f("ix_credit_transactions_account_id"), table_name="credit_transactions"
    )
    op.drop_table("credit_transactions")
    op.drop_index(op.f("ix_cart_items_menu_item_id"), table_name="cart_items")
    op.drop_index(op.f("ix_cart_items_menu_id"), table_name="cart_items")
    op.drop_index(op.f("ix_cart_items_cart_id"), table_name="cart_items")
    op.drop_table("cart_items")
    op.drop_index(
        "uq_subscription_skip_date",
        table_name="subscription_events",
        postgresql_where=sa.text("event_type = 'skip'"),
    )
    op.drop_index(
        op.f("ix_subscription_events_subscription_id"), table_name="subscription_events"
    )
    op.drop_index(
        op.f("ix_subscription_events_actor_user_id"), table_name="subscription_events"
    )
    op.drop_table("subscription_events")
    op.drop_index(
        op.f("ix_subscription_credits_user_id"), table_name="subscription_credits"
    )
    op.drop_table("subscription_credits")
    op.drop_index(op.f("ix_orders_user_id"), table_name="orders")
    op.drop_index(op.f("ix_orders_status"), table_name="orders")
    op.drop_index(op.f("ix_orders_menu_id"), table_name="orders")
    op.drop_index(op.f("ix_orders_delivery_slot_id"), table_name="orders")
    op.drop_index(op.f("ix_orders_business_date"), table_name="orders")
    op.drop_index(op.f("ix_orders_address_id"), table_name="orders")
    op.drop_table("orders")
    op.drop_index(op.f("ix_menu_items_menu_id"), table_name="menu_items")
    op.drop_index(op.f("ix_menu_items_food_item_id"), table_name="menu_items")
    op.drop_table("menu_items")
    op.drop_index(op.f("ix_subscriptions_user_id"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_status"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_renewed_from_id"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_plan_id"), table_name="subscriptions")
    op.drop_table("subscriptions")
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_status"), table_name="notifications")
    op.drop_table("notifications")
    op.drop_index(op.f("ix_food_items_category_id"), table_name="food_items")
    op.drop_table("food_items")
    op.drop_table("customer_profiles")
    op.drop_index(op.f("ix_carts_menu_id"), table_name="carts")
    op.drop_table("carts")
    op.drop_index(op.f("ix_audit_logs_target_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_actor_user_id"), table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index(
        "uq_addresses_one_live_default",
        table_name="addresses",
        postgresql_where=sa.text("is_default AND deleted_at IS NULL"),
    )
    op.drop_index(op.f("ix_addresses_user_id"), table_name="addresses")
    op.drop_table("addresses")
    op.drop_table("users")
    op.drop_table("subscription_plans")
    op.drop_table("food_categories")
    op.drop_table("delivery_slots")
    op.drop_table("daily_menus")
    # ### end Alembic commands ###
```

### scripts/start-api.ps1

```powershell
[CmdletBinding()]
param([ValidateRange(1024, 65535)][int]$Port = 8000)
$ErrorActionPreference = 'Stop'
$backend = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$python = Join-Path $backend '.venv/Scripts/python.exe'
$local = Join-Path $backend '.local'
$recordPath = Join-Path $local 'api.process.json'
if (-not (Test-Path -LiteralPath $python)) { throw 'Install the backend virtual environment first.' }
New-Item -ItemType Directory -Force -Path $local | Out-Null
if (Test-Path -LiteralPath $recordPath) {
    $record = Get-Content -Raw -LiteralPath $recordPath | ConvertFrom-Json
    $existing = Get-Process -Id $record.pid -ErrorAction SilentlyContinue
    if ($existing -and $existing.StartTime.ToUniversalTime().Ticks.ToString() -eq $record.startedTicks) {
        Write-Output "Managed API already running at http://127.0.0.1:$($record.port)/docs"
        exit 0
    }
}
$listener = [Net.Sockets.TcpClient]::new()
try {
    try { $listener.Connect('127.0.0.1', $Port) } catch { }
    if ($listener.Connected) { throw "Port $Port is already in use. No existing process was stopped. Choose another -Port." }
} finally { $listener.Dispose() }
$stamp = Get-Date -Format 'yyyyMMdd-HHmmssfff'
$stdout = Join-Path $local "api-$stamp.stdout.log"
$stderr = Join-Path $local "api-$stamp.stderr.log"
$process = Start-Process -FilePath $python -ArgumentList @(
    '-m', 'uvicorn', 'app.main:app', '--app-dir', ('"' + $backend + '"'),
    '--host', '127.0.0.1', '--port', $Port.ToString(), '--no-proxy-headers'
) -WorkingDirectory $backend -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
@{ pid = $process.Id; port = $Port; startedTicks = $process.StartTime.ToUniversalTime().Ticks.ToString(); stdout = $stdout; stderr = $stderr } |
    ConvertTo-Json | Set-Content -LiteralPath $recordPath -Encoding utf8
$watch = [Diagnostics.Stopwatch]::StartNew()
while ($watch.Elapsed.TotalSeconds -lt 30) {
    $process.Refresh()
    if ($process.HasExited) { throw "API exited. Check $stderr" }
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/v1/health" -TimeoutSec 1
        if ($health.status -eq 'ok') {
            Write-Output "API started at http://127.0.0.1:$Port/docs"
            exit 0
        }
    } catch { }
    Start-Sleep -Milliseconds 250
}
throw "API startup timed out. Check $stderr"
```

### scripts/start-postgres.ps1

```powershell
# Local portable installation created during Phase 4; no Windows service.
$ErrorActionPreference = 'Stop'
$pgBin = Join-Path $env:LOCALAPPDATA 'DailyDabba/postgresql-17/pgsql/bin'
$pgData = Join-Path $env:LOCALAPPDATA 'DailyDabba/pgdata17'
if (-not (Test-Path (Join-Path $pgBin 'pg_ctl.exe'))) {
    throw 'Portable PostgreSQL is not installed here. See docs/database-setup.md for Docker or installer setup.'
}
& (Join-Path $pgBin 'pg_ctl.exe') -D $pgData status
if ($LASTEXITCODE -eq 0) { exit 0 }
& (Join-Path $pgBin 'pg_ctl.exe') -D $pgData -l (Join-Path $env:LOCALAPPDATA 'DailyDabba/postgresql.log') -t 120 -w start
exit $LASTEXITCODE
```

### scripts/stop-api.ps1

```powershell
$ErrorActionPreference = 'Stop'
$backend = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$recordPath = Join-Path $backend '.local/api.process.json'
if (-not (Test-Path -LiteralPath $recordPath)) { Write-Output 'No managed API record.'; exit 0 }
$record = Get-Content -Raw -LiteralPath $recordPath | ConvertFrom-Json
$process = Get-Process -Id $record.pid -ErrorAction SilentlyContinue
if (-not $process) { Write-Output 'Managed API is already stopped.'; exit 0 }
if ($process.StartTime.ToUniversalTime().Ticks.ToString() -ne $record.startedTicks) {
    throw 'The recorded process ID was reused; refusing to stop anything.'
}
$details = Get-CimInstance Win32_Process -Filter "ProcessId=$($record.pid)"
if (-not $details.CommandLine.Contains($backend) -or -not $details.CommandLine.Contains('uvicorn')) {
    throw 'Process identity does not match this backend; refusing to stop anything.'
}
& taskkill.exe /PID $record.pid /T /F | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Could not stop the managed API.' }
Write-Output 'Stopped this backend API. PostgreSQL remains running.'
```

### scripts/stop-postgres.ps1

```powershell
$ErrorActionPreference = 'Stop'
$pgBin = Join-Path $env:LOCALAPPDATA 'DailyDabba/postgresql-17/pgsql/bin'
$pgData = Join-Path $env:LOCALAPPDATA 'DailyDabba/pgdata17'
& (Join-Path $pgBin 'pg_ctl.exe') -D $pgData -m fast -w stop
exit $LASTEXITCODE
```

## Monorepo infrastructure source

These paths are relative to the parent dailydabba directory.

### .env.example

```text
# Docker-only bootstrap credentials; the application must not use this account.
POSTGRES_USER=postgres
POSTGRES_PASSWORD=replace_admin_password
POSTGRES_DB=dailydabba
POSTGRES_PORT=5432
# These must match backend/.env migration and runtime URLs respectively.
MIGRATION_DB_PASSWORD=replace_migration_password
APP_DB_PASSWORD=replace_app_password
```

### docker-compose.yml

```yaml
name: dailydabba

services:
  postgres:
    image: postgres:17-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:?Copy .env.example to .env and set POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD in .env}
      POSTGRES_DB: ${POSTGRES_DB:?Set POSTGRES_DB in .env}
      MIGRATION_DB_PASSWORD: ${MIGRATION_DB_PASSWORD:?Set MIGRATION_DB_PASSWORD in .env}
      APP_DB_PASSWORD: ${APP_DB_PASSWORD:?Set APP_DB_PASSWORD in .env}
    ports:
      - "127.0.0.1:${POSTGRES_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/docker/initdb:/docker-entrypoint-initdb.d:ro
    command: ["postgres", "-c", "timezone=UTC"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \"$$POSTGRES_USER\" -d \"$$POSTGRES_DB\""]
      interval: 5s
      timeout: 5s
      retries: 10
      start_period: 10s

volumes:
  postgres_data:
```

### infrastructure/docker/.gitattributes

```text
initdb/*.sh text eol=lf
```

### infrastructure/docker/initdb/01_roles.sh

```sh
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
```

## Repository-root ignore file

Path: C:/Users/rmshr/OneDrive/Desktop/food_startup/.gitignore

```text
# Repository-wide dependency and secret exclusions
node_modules/
.env
.env.*
!.env.example
```
