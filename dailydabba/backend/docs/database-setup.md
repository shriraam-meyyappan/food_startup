# Phase 4: PostgreSQL, sessions and Alembic

Phase 3 is confirmed. Phase 4 is implemented and verified against PostgreSQL
17.12. The development database now has 23 application tables plus Alembic's
version table at revision `0001_initial`. There is no customer/business data.
No authentication, payment API or other later-phase feature has been implemented.

## This machine: ready to use

PostgreSQL was installed from the official Windows binary archive under:
`C:/Users/rmshr/AppData/Local/DailyDabba/postgresql-17/pgsql/bin`.
Data is in `C:/Users/rmshr/AppData/Local/DailyDabba/pgdata17`, outside the repository
and OneDrive. It listens on `127.0.0.1:55432`, uses SCRAM password authentication
and UTC, and is currently running. No Windows service or PATH change was made.
It does not automatically start after reboot.

Backend `.env` is already configured with generated local passwords. The local
bootstrap admin password is stored in ignored `.local/postgres-admin.password` for
local administration only. Neither file is committed or reproduced in documentation.
Do not overwrite your existing `.env` with the example.

From `C:/Users/rmshr/OneDrive/Desktop/food_startup/dailydabba/backend`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m app.db.check
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Expected database check:

```json
{"status":"ready","timezone":"UTC","revision":"0001_initial"}
```

Stop any older development API server with Ctrl+C and start it again so the new
configuration is loaded. In a second terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/ready
```

Health remains `{"status":"ok"}`. Readiness should now be `{"status":"ready"}`.
Readiness checks a database query, UTC and the current migration revision. If
configuration is absent, the database is stopped, credentials are wrong, or the
migration is missing/outdated, readiness returns HTTP 503 with only
`{"detail":"Database unavailable"}`. Health remains independent of the database.
Both routes appear in `/docs`. No browser pages or customer-facing screens were added.

## Starting and stopping local PostgreSQL

After a reboot, start the installed database directly (no script policy change):

```powershell
$pgBin = Join-Path $env:LOCALAPPDATA 'DailyDabba/postgresql-17/pgsql/bin'
$pgData = Join-Path $env:LOCALAPPDATA 'DailyDabba/pgdata17'
& (Join-Path $pgBin 'pg_ctl.exe') -D $pgData -l (Join-Path $pgData 'server.log') -w start
```

Stop it when no developer needs it:

```powershell
& (Join-Path $pgBin 'pg_ctl.exe') -D $pgData -m fast -w stop
```

Equivalent local helpers are `scripts/start-postgres.ps1` and
`scripts/stop-postgres.ps1`. They target only the installation above, do not download
software, and do not change the PowerShell execution policy. If scripts are blocked,
use the explicit executable commands instead.

Other team members should use Docker below or an installed PostgreSQL 17 server;
these user-specific native paths will not exist on their machines. The native
installation is persistent, not dependent on the downloaded temporary ZIP file.

## Team option: Docker PostgreSQL

Docker Desktop is NOT installed here, so the container launch has not been tested
on this machine. Native PostgreSQL has been fully tested. The monorepo Compose
configuration supports a separate Docker installation on port 5432 by default.
Choose one server for a given backend `.env`.

From the `dailydabba` directory on a machine with Docker Desktop/Linux containers:

```powershell
# Copy only if no existing root .env exists.
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edit root `.env`: choose distinct admin, migration and application passwords.
Keep `POSTGRES_USER=postgres`, `POSTGRES_DB=dailydabba`, and choose the host port.
The application must never use the admin account. Then:

```powershell
docker compose up -d --wait postgres
docker compose ps
```

The fresh-volume initialization script creates `dailydabba_migrator` and
`dailydabba_app`, and development/test databases owned by the migration role.
It revokes PUBLIC schema creation and grants only schema usage/connection to the
application role. Alembic grants explicit table permissions after creating tables.
Shell files are kept with LF endings for Linux containers.

Configure backend `.env` from `.env.example` using those same migration/application
passwords, database name and host port. URL-encode reserved password characters.
Then run `python -m alembic upgrade head` from the backend using its virtual Python.
The commented test URL must point to the separate `dailydabba_test` database.

Existing Compose volumes are preserved. Init scripts run only when a volume is
empty; changing `.env` does not rotate existing passwords or create missing roles.
For an existing database, use explicit reviewed administration, or provision a new
separate volume/project. Do not delete an existing volume to fix a configuration error.
The old NestJS `.env` is separate and is not used by the Python application.

## Using another native PostgreSQL installation

Install PostgreSQL 17 from [the official Windows page](https://www.postgresql.org/download/windows/).
Set backend `DATABASE_URL` and `MIGRATION_DATABASE_URL` first, using the documented
role names, distinct passwords and the same server/port. To provision fresh local
development/test databases with an admin account, set `BOOTSTRAP_DATABASE_URL` in
that terminal's environment (not in tracked files or the backend `.env`) and run:

```powershell
.\.venv\Scripts\python.exe -m app.db.provision --database dailydabba
.\.venv\Scripts\python.exe -m app.db.provision --database dailydabba_test
Remove-Item Env:BOOTSTRAP_DATABASE_URL
.\.venv\Scripts\python.exe -m alembic upgrade head
```

The provisioner refuses to take over a database owned by another role, only accepts
the two documented database names, and does not change existing role passwords.
Do not point it at a shared or production database. PostgreSQL admin privileges are
needed only for provisioning; the migration/application accounts are not superusers
and cannot create databases or roles. Production provisioning is a separate reviewed
operations task, not a use of these local convenience scripts.

## Connection and session architecture

`app/core/config.py` validates PostgreSQL+Psycopg URLs. They are SecretStr fields
excluded from settings repr; validation messages hide raw inputs. The application
uses only DATABASE_URL, while Alembic requires MIGRATION_DATABASE_URL and never
falls back to runtime credentials. In production, supply migration credentials only
to the migration job, not to the API process. Both appear in local `.env` only for
developer convenience.

`Database.from_url()` creates a synchronous SQLAlchemy engine with pre-ping,
bounded pool, five-second connect timeout, UTC sessions and hidden SQL parameters.
Constructing an engine is lazy and does not open a connection. Application lifespan
creates the engine and disposes it on shutdown. It never creates tables or migrates.

`get_session()` is a FastAPI generator dependency; `DbSession` is its reusable type
alias. A request receives one session. Failed requests roll back; closing a session
also rolls back unfinished work. No automatic commit is performed. Future services
must explicitly commit one whole operation with `with session.begin(): ...`.
A SQLAlchemy session tracks pending changes; `flush()` sends SQL inside the current
transaction, whereas `commit()` makes that transaction persistent.

Keep synchronous database work in synchronous route/service functions. Sessions
must not be shared across requests or threads. Tests override dependencies only in
test applications, never in the running API.

## Migrations: versioned changes to the database

A migration is a reviewed, versioned schema change, similar to a code change.
Alembic tracks the applied revision in `alembic_version`. The initial migration
contains frozen table/index/constraint operations and explicit runtime grants.
It imports no current model metadata, so later model changes cannot rewrite history.

Common commands (backend directory):

```powershell
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic history
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic check
```

`upgrade head` applies unapplied revisions once. `check` compares the current model
metadata with the database for schema differences. The current expected result is
`No new upgrade operations detected.` Autogenerate cannot validate business rules,
permission correctness or every constraint change; human review and tests remain
required.

For a future approved schema change: edit models, generate a NEW revision using
`alembic revision --autogenerate -m "describe change"`, review the complete upgrade
and downgrade, test on a scratch database, and then apply it. Never edit an already
applied migration, blindly stamp a version, or use `create_all()` on startup.

PostgreSQL migration DDL runs transactionally. The integration suite exercises
upgrade -> downgrade -> upgrade on the test database. Downgrading the initial
migration drops all application tables and destroys their data; NEVER run that on
the development database merely to repeat a test. For populated databases, take and
verify a backup before migration and prefer a forward corrective migration if
rollback would lose data. Follow expand/backfill/contract steps for incompatible
changes. Full deployment and backup automation remain Phase 15.

## Runtime permissions and remaining boundaries

The migration role owns schema objects; the application does not. Runtime can read
and insert application records, but cannot create/drop tables or change Alembic's
version. Immutable ledger, audit, subscription-event and order-item records have no
runtime UPDATE or DELETE. Orders allow UPDATE only on status; purchased price,
address and delivery snapshots cannot be edited through the runtime account.
Payment/refund/account updates are restricted to specific lifecycle/balance columns.
Only explicit migration grants enable a future table; there are no broad default
privileges granting the application control over unknown future tables.

These are database-level guards against accidental mutation by application code.
A database owner/superuser can still change history. They do not implement
row-level user authorization, valid order transitions, complete append-only order
collections, cross-row totals, refund limits, credit ledger/balance agreement or
concurrent credit redemption. Those require the future authenticated services and
reviewed transaction policies. Model foreign keys ensure related ownership is
consistent; they are not an access-control system for reading customer records.

## Tests

```powershell
# No database is required; integration checks are explicitly skipped.
.\.venv\Scripts\python.exe -m pytest -q

# Real PostgreSQL checks: DESTRUCTIVE ONLY to the dedicated scratch test database.
.\.venv\Scripts\python.exe -m pytest -q --run-db
```

Expected: ordinary run `18 passed, 14 skipped`; with `--run-db`, `32 passed`.
One existing upstream Starlette/AnyIO deprecated-alias warning remains.
`TEST_DATABASE_URL` must be configured. Tests refuse any database name except
`dailydabba_test`, refuse the development database, and refuse unknown tables.
They reset test schema/data and downgrade it after finishing. Do not keep useful
data in that scratch database. Development tables/data are never reset by tests.

Coverage includes migration roundtrip and drift, real PostgreSQL CHECK/unique/
foreign-key enforcement, exact/computed prices, order snapshots, owned addresses,
default-address uniqueness, nonnegative credits, duplicate grants/request keys,
provider ID uniqueness, invalid refund amounts, UTC, runtime permission denials,
readiness and request rollback. No payment provider is contacted. Credit business
policies and concurrency services have not been implemented or certified.

## Verified outcome and next step

The native PostgreSQL database was migrated and checked using limited runtime
credentials. The full 32-test run passed, and runtime readiness reports UTC at
revision `0001_initial`. The test database was returned to base; the development
database remains migrated and PostgreSQL remains running locally.

Review this guide, run the readiness/test commands, and explicitly confirm Phase 4
before Phase 5 (registration, login, Argon2, JWT and role-based authorization).
Both frontend apps remain unchanged. Current source work remains uncommitted.

References: [SQLAlchemy PostgreSQL](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html),
[Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html),
[official Windows binaries](https://www.enterprisedb.com/download-postgresql-binaries).
