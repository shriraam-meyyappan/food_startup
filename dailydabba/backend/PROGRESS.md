# DailyDabba backend progress

Updated: 12 November 2026 (Asia/Kolkata).

## Confirmation history
- Active backend: dailydabba/backend (Python/FastAPI).
- User confirmed Phases 1 and 2 via health and explicitly approved continuation.
- User confirmed Phase 3 with 14 passing tests and one known warning, then approved Phase 4.
- Phase 4 is now implemented and verified; awaiting explicit confirmation.
- No Phase 5–15 feature work has started. Both frontend applications are untouched.
- Historical services/api (NestJS/Prisma) remains preserved and is not the active backend.

## Completed phases
1. Python environment, FastAPI, configuration, UTC logging, health and tests.
2. Backend boundaries, central version router and architecture guide.
3. 23 SQLAlchemy models, database design/ER diagram, exact money/timestamps,
   constraints, offline DDL exporter, SQL examples and model checks.
4. PostgreSQL/Psycopg connection, scoped sessions, migration credentials, Alembic
   initial migration/runtime grants, readiness, real DB tests and local/team setup.

## Current local database
- PostgreSQL 17.12 installed from official EDB binaries, not a Windows service.
- Binaries: C:/Users/rmshr/AppData/Local/DailyDabba/postgresql-17/pgsql/bin.
- Data: C:/Users/rmshr/AppData/Local/DailyDabba/pgdata17 (outside repo and OneDrive).
- Currently running on 127.0.0.1:55432; SCRAM authentication; UTC sessions.
- Backend .env has generated runtime/migration/test URLs, all ignored by Git.
- Local bootstrap password: ignored backend/.local/postgres-admin.password.
- Development database: dailydabba, revision 0001_initial, 23 application tables
  plus alembic_version. No customer/business records were seeded.
- Dedicated disposable database: dailydabba_test. Integration tests return it to
  base; they never reset development data. PostgreSQL does not auto-start on reboot.
- Docker is absent. Updated Compose/bootstrap scripts are supplied and shell syntax
  checked; actual container launch is unverified. Use the verified native setup here.

## Phase 4 files
Created:
- app/db/database.py, check.py, provision.py: engine/sessions, safe checks, explicit admin provisioning.
- app/api/v1/readiness.py: sanitized readiness HTTP endpoint.
- alembic.ini, alembic/env.py, alembic/script.py.mako, and the frozen
  alembic/versions/0001_initial_initial_database_schema.py migration.
- app/tests/conftest.py, test_database_unit.py, test_database_integration.py.
- scripts/start-postgres.ps1, scripts/stop-postgres.ps1.
- docs/database-setup.md with exact setup/run/migration/test commands and safeguards.
- infrastructure/docker/initdb/01_roles.sh and .gitattributes for Linux line endings.
Modified:
- Settings, lifespan, version router, health schemas, database package description.
- requirements.in/requirements.txt: Alembic 1.20.1, Psycopg 3.3.9 binary package and dependencies.
- Safe backend/root .env examples, backend ignore rules, Compose role/bootstrap setup.
- READMEs, architecture/database guides and this progress summary.
- Local .env gained real URLs without printing passwords or overwriting prior settings.

## Current APIs
- GET /api/v1/health: HTTP 200 {"status":"ok"}; process liveness only.
- GET /api/v1/ready: HTTP 200 {"status":"ready"}; queries PostgreSQL, verifies UTC
  and current migration head. Missing/unavailable/outdated DB returns sanitized 503.
- /docs and /openapi.json include both operations.
- No registration/login or business API exists yet. The user must restart an older
  API instance to load new settings; the verification API process was stopped afterward.

## Sessions and permissions
- Engine is lazy, uses pre-ping, a bounded pool, timeout, UTC and hidden SQL parameters.
- Each request gets a separate session; failures/uncommitted work roll back on close.
- Future services explicitly own transaction commits. No startup create_all/migrations.
- Migration role owns objects; runtime role is not superuser/schema owner.
- Runtime cannot DDL or alter Alembic's revision record. It can read the version for readiness.
- Runtime has no update/delete on ledger, audit, subscription-event or order-item history.
- Order snapshots/amounts are protected by column-level updates (status only).
- Other financial records have narrow lifecycle/balance column updates; no deletes.
- Owners/superusers can still modify history. These controls do not implement row-level
  authorization, full order collection immutability, ledger reconciliation, credit
  concurrency rules, state transitions or refund policies. Those remain feature work.

## Verified in Phase 4
- Dependency consistency passed.
- 32 tests passed with --run-db (18 ordinary checks and 14 PostgreSQL integration cases).
- Ordinary pytest intentionally skips integration: expected 18 passed, 14 skipped.
- Upgrade/downgrade/upgrade on dedicated test DB; final test DB returned to base.
- Development migration applied; Alembic check found no schema drift.
- Real CHECK/unique/composite foreign-key enforcement, exact/generated prices,
  snapshot persistence, owned addresses, default uniqueness, nonnegative credits,
  duplicate grants/order request keys/provider IDs, and invalid refunds tested.
- Runtime DDL/history mutation/version mutation denials verified; failed HTTP request rollback tested.
- Live health, readiness, Swagger HTML and OpenAPI each returned HTTP 200.
- Local provisioning was safely rerun without password rotation or ownership takeover.
- Runtime CLI check returned ready, UTC, 0001_initial.
- One existing upstream Starlette/AnyIO deprecated-alias warning remains, not a failure.
- Frontend apps and legacy NestJS starter unchanged. Credentials, data, environment,
  virtual environment and caches are not staged/tracked. Work remains uncommitted.

## Team confirmation checklist
- [ ] Read docs/database-setup.md and understand native versus Docker setup.
- [ ] Restart the API, then GET /api/v1/ready; expect {"status":"ready"}.
- [ ] Run python -m app.db.check with the virtual environment; expect UTC and 0001_initial.
- [ ] Run Pytest with --run-db; expect 32 passing tests and the known warning.
- [ ] Keep useful data out of dailydabba_test; tests intentionally reset its schema.
- [ ] Explicitly confirm Phase 4 before Phase 5.

## Unresolved future business policies
One role/user and one dated meal menu/order are initial design choices. Credit-to-
meal mapping, combined accounts, partial restores, skip deadlines, pause extensions,
fulfillment deduction timing, tax/fee values and refund rules remain unapproved.
Do not invent those policies during authentication or database work.

## Next phase (not started)
Phase 5: registration, login, Argon2 hashing, JWT access/verification, current-user
lookup, profile retrieval/updates and customer/admin/kitchen role authorization.
Keep this backend-only and stop for confirmation after the phase.

## Continue in another chat
Read this file, README.md and docs/database-setup.md first; then architecture/design
and actual source/migrations. Inspect Git status and preserve all existing work.
Do not edit already-applied migration 0001_initial, delete local data, reset the
user's server or advance phases without explicit approval. No frontend changes.
