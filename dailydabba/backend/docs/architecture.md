# Backend architecture (updated through Phase 4)

Phases 2 and 3 were confirmed by the team. Phase 4 now supplies PostgreSQL
engine/session dependencies, database readiness, Alembic migrations and restricted
runtime permissions. See [database setup](database-setup.md) and
[database design](database-design.md) for the current verified state.

The active backend is `dailydabba/backend`. It is a modular monolith: one Python
application, one deployment unit, and (in a later phase) one PostgreSQL database.
Each folder has a narrow role so four developers can work on separate features
without placing everything in a single file. SQLAlchemy 2.0, Psycopg 3 and Alembic provide persistence and migrations.

## Current structure and responsibilities

```text
backend/
  app/
    main.py                  Builds FastAPI and configures startup/shutdown
    core/
      config.py              Validates environment configuration
      logging.py             Configures UTC console logging
    api/
      v1/
        router.py            Registers all version 1 feature routers
        health.py            Serves the liveness HTTP endpoint
        readiness.py         Verifies database/migration readiness
    schemas/
      health.py              Defines the public health JSON contract
    db/base.py               Declarative base and record mixin
    db/database.py           Engine and request session dependency
    db/check.py              UTC/connectivity/migration check
    db/provision.py          Explicit local admin provisioning
    db/export_schema.py      Offline PostgreSQL schema export
    models/                  Mapped identity, catalog, commerce, subscription,
                             payment and operations tables
    services/__init__.py     Reserved package for business use cases
    repositories/__init__.py Reserved package for database queries
    tests/                   Automated endpoint and configuration checks
  docs/architecture.md       This architecture guide
  .env.example               Safe configuration sample
  .env                       Local settings, ignored by Git
  .gitignore                 Python and local-file exclusions
  requirements.in            Direct dependencies and compatibility constraints
  requirements.txt           Exact tested dependency versions
  pytest.ini                 Test discovery settings
  README.md                  Setup, commands, expected outputs, complete code
  PROGRESS.md                Phase history and next-chat handoff
```

Services and repositories remain documentation-only package boundaries. Models
now describe 23 tables and db/base.py supplies metadata. Imports do not create tables or open connections. Lifespan configures a lazy
engine; request dependencies open scoped sessions. Business operations remain later.

### Application entry point

`app/main.py` creates the application through `create_app()`. It attaches the
version 1 router and manages startup/shutdown logging. It should stay small as
features are added. Tests can create a separate application with test settings.

### HTTP routes and version registration

`app/api/v1/router.py` is the single registration point for version 1 endpoints.
It owns the `/api/v1` prefix and includes each feature router once. The health
router declares only `/health`, producing `/api/v1/health`.

A route accepts validated inputs, calls a service when business logic exists,
and returns a response schema. Routes will own HTTP-specific concerns such as
status codes and FastAPI dependencies. Future service code must not import routes.
FastAPI's supported router composition is described in its official guide:
https://fastapi.tiangolo.com/tutorial/bigger-applications/

### Schemas versus models

`app/schemas` holds Pydantic request and response classes: the data an API accepts
or exposes. `HealthResponse` currently restricts status to the literal `ok`.

`app/models` holds SQLAlchemy classes describing database records and their
relationships. Database models and API schemas have different jobs. For example,
a future user database record may contain a password hash, but its public response
schema must never expose that field. User storage is now modeled, but no registration or authentication service exists.

### Services

`app/services` will coordinate business use cases and rules. For example, a future
order service would validate availability and calculate a total using server-side
prices. This is an illustration of responsibility, not an order design or API.
Services should take explicit inputs rather than HTTP request objects.

Use ordinary functions initially; introduce a class only when it simplifies shared
state or dependencies. Do not add base-service classes or an interface for every
function.

### Repositories

`app/repositories` will contain SQLAlchemy queries and persistence operations for
real features. Repositories receive a session from the caller; they do not create
global sessions, return HTTP responses, or decide business policies. Do not wrap
every SQLAlchemy method in an abstract generic repository. Add a small concrete
query function when a feature needs one.

### Database infrastructure

`app/db/base.py` now provides the SQLAlchemy declarative base and named metadata.
The offline exporter compiles review-only DDL. The engine/session factory and
request-scoped session dependency now connect to PostgreSQL through Psycopg.
Alembic manages schema changes explicitly; startup does not run migrations.

Current convention: use synchronous SQLAlchemy 2.0 sessions and synchronous
routes for database work. This keeps transaction handling straightforward for a
Python team. Do not call blocking database operations directly from an async route.
Psycopg 3 and tested dependency versions are pinned in requirements.txt.

The request dependency opens/closes a session and rolls back unfinished work. A service will own the transaction
boundary for its use case: succeed together or roll back together. Repositories
may flush work but must not independently commit partial changes. Request rollback is now verified; business-level transactions remain feature work.

### Configuration, security and reusable helpers

`app/core/config.py` is the configuration boundary. New settings should be typed
and validated there when a feature actually needs them. Secrets belong in local
environment files or deployment secret storage, never in source or API responses.
`app/core/logging.py` defines UTC console logging.

Add `core/security.py` when authentication is implemented in Phase 5. Creating an
empty security helper now could imply protection that does not exist. Similarly,
add `utils/` only for a genuinely shared, narrowly named helper; business rules
belong with their service rather than in a miscellaneous utility module.

### Tests and migrations

`app/tests` currently checks HTTP contracts and configuration. Later service tests
will exercise business rules, and database integration tests will use an isolated
test database. Test data must never share the production database.

Alembic now has a frozen initial migration and model metadata for future
autogenerate checks. Do not call `create_all()` at application startup or treat the
existing Prisma schema as the Python backend's migration history.

## Request flow

This is the implemented health request path:

```mermaid
flowchart LR
    A[GET /api/v1/health] --> B[FastAPI application]
    B --> C[Version 1 router]
    C --> D[Health route]
    D --> E[HealthResponse schema]
    E --> F[HTTP 200 JSON]
```

The health route needs no service, repository, or database query: it reports that
the process can serve requests. Database readiness will be a separate concern.

For later database-backed features, the planned flow is:

1. FastAPI validates incoming data using a request schema.
2. The route receives dependencies such as a database session and current user.
3. The route calls the feature's service with explicit arguments.
4. The service applies business rules and coordinates its transaction.
5. Repository functions query/update SQLAlchemy models through the supplied session.
6. The service returns the result; the route exposes only its response schema.

Dependency direction is deliberate: routes may depend on services and schemas;
services may depend on repositories and models; repositories may depend on models
and the session API. Lower layers must not import `main.py`, route modules, or
HTTP response types. Configuration can be used where needed without circular imports.

Expected business failures will later be translated to HTTP errors at the API
boundary. Unexpected failures must not expose database errors or credentials.
Do not introduce a custom exception framework before a feature needs it.

## Why this differs from the example structure

We keep `backend/` inside the existing monorepo instead of replacing historical
work. A version router gives endpoint registration a dedicated home. Package
markers establish future persistence/business boundaries without premature ORM
code. Security, utility helpers, and Alembic files are deferred to their actual
implementation phases. No microservices, generic abstraction layer, or dependency
injection container is needed; FastAPI dependencies will supply request resources.

## Team workflow and verification

One developer can work on route/schema contracts, another on confirmed models and
migrations, another on services/repositories, and another on tests and integration.
These are suggested ownership areas for future work, not permission to start all
phases at once. Agree on request/response contracts before splitting a feature.
Review transaction ownership and public response fields together.

From the backend directory, use the same commands as Phase 1:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Expected: no broken requirements, 18 passing ordinary tests (14 database tests
skipped), and a running local server. Use --run-db for all 32 tests.
Then check `/api/v1/health` for HTTP 200 and `{"status":"ok"}`, and open `/docs`.
The test-tool deprecation warning documented in the README is unchanged.

Phase 3 now defines models and review-only schema SQL; the development database is now migrated in Phase 4. No new business APIs exist. Complete source code is in the README.
Phase 4 connections, sessions, migrations and database tests are now verified.
Phase 5 authentication awaits team confirmation.
