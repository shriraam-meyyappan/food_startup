# DailyDabba backend progress

Updated: 13 November 2026 (Asia/Kolkata).

## Current authorization and state
- User could not check Phase 4 and explicitly asked the agent to verify/repair it,
  then execute Phase 5 and provide a detailed completed-work/remaining plan.
- Phase 4 was restored and reverified before Phase 5: all original 32 tests passed.
- Phase 5 is implemented and verified: 80 tests pass with one known library warning.
- Phase 6 has NOT started; wait for explicit confirmation.
- Active backend: dailydabba/backend. Legacy services/api is preserved historical work.
- Both frontend apps remain untouched; no layouts/screens/branding were added.
- Detailed handoff: docs/implementation-summary.md. Auth walkthrough: docs/authentication.md.

## Current running services
- PostgreSQL 17.12: 127.0.0.1:55432, SCRAM authentication, UTC sessions.
- Binaries: C:/Users/rmshr/AppData/Local/DailyDabba/postgresql-17/pgsql/bin.
- Data: C:/Users/rmshr/AppData/Local/DailyDabba/pgdata17 (outside repo/OneDrive).
- Startup log now C:/Users/rmshr/AppData/Local/DailyDabba/postgresql.log, OUTSIDE data.
- API was started as a managed hidden local process on http://127.0.0.1:8000.
- Swagger: /docs. Ignored .local/api.process.json records PID/start identity/log paths.
- scripts/start-api.ps1 and stop-api.ps1 safely manage only this workspace's API.
- Neither service auto-starts after reboot. Managed API has no automatic reload.
- Local secrets stay in ignored backend/.env and .local/postgres-admin.password.
- No real JWT key, password or token is printed in source/documentation.

## Phase 4 recheck/repair for this request
- PostgreSQL was stopped. Startup recovered from an earlier interruption.
- Windows reported a sharing conflict with the old log in the data directory,
  delaying recovery. Recovery completed; then a clean restart used the external log.
- Start helper now allows 120 seconds for recovery. No data directory was reset.
- No API listener existed on port 8000. The verified Phase 5 API is now running there.
- Database readiness and live HTTP endpoints were verified.
- Original schema still has 23 application tables plus alembic_version at 0001_initial.
- No schema drift; no applied migration was edited, and Phase 5 needed no new migration.

## Completed history
0. Initial monorepo: independent Next.js/Flutter/NestJS starters, infrastructure,
   examples/ignore rules/docs and commit ae4cd0e. Later backend direction changed
   explicitly to Python; NestJS remains historical scaffolding.
1. Python 3.13.5 venv, FastAPI, configuration, UTC logging, health, docs and six tests.
2. Central version router, architecture responsibilities and package boundaries.
3. 23 SQLAlchemy models, ER diagram, exact money/time/ownership constraints,
   credit ledger design, offline SQL compiler, SQL examples and model tests.
4. Psycopg, native PostgreSQL, scoped sessions, separate migration/runtime roles,
   Alembic initial migration, readiness, permissions and real DB integration tests.
5. Registration/login, Argon2, signed JWTs, current-user/self-profile APIs,
   role checks, staff-account command, safe errors, auth throttle and extensive tests.

## Phase 5 API contracts
- GET /api/v1/health -> {"status":"ok"}.
- GET /api/v1/ready -> {"status":"ready"}; unavailable/unmigrated DB -> sanitized 503.
- POST /api/v1/auth/register -> 201 customer + profile; duplicate email 409.
- POST /api/v1/auth/login -> 200 bearer access token, expires_in 900 by default.
- GET /api/v1/users/me -> authenticated current account/profile only.
- PATCH /api/v1/users/me/profile -> own full_name/phone only; phone null clears it.
- GET /api/v1/admin/access-check -> admins 200, other authenticated roles 403.
- GET /api/v1/kitchen/access-check -> admin/kitchen staff 200, customers 403.
- Anonymous/invalid/expired token gets 401 with WWW-Authenticate: Bearer.
- Invalid inputs 422, throttle 429/Retry-After, unavailable auth/DB 503.
- API responses are no-store. These are JSON backend APIs, not dashboard operations.

## Security and transaction decisions
- Public registration always assigns customer; unknown/privileged fields rejected.
- Emails are lowercase and unique. ON CONFLICT handles simultaneous registration.
- Argon2id hashes only; successful login upgrades older hash parameters as needed.
- Key is cryptographically generated into ignored .env; fixed HS256 allowlist.
- Verify exp/iat/nbf/iss/aud/sub/jti/token_type and UUID subjects/JWT IDs.
- JWT carries identity, NOT a trusted role. Query current DB role/status each request.
- Disabled/deactivated users cannot log in or reuse otherwise valid access tokens.
- Staff CLI prompts twice and requires trusted migration credentials. Existing
  accounts are never silently promoted/replaced. No default admin was created.
- Registration/profile/staff changes include minimal audit entries in the same commit.
- Audit details do not contain passwords, tokens or private profile values.
- Repositories do not commit. Services coordinate transactions; request sessions
  roll back unfinished/failed work. SQL parameters and validation inputs are hidden.
- Request validation responses never include submitted input/context values.
- Auth limits are bounded/thread-safe/process-local, default 10/minute per endpoint
  and ASGI client address. Local server disables proxy header interpretation.

## Phase 5 files created
- core/security.py, core/errors.py, core/rate_limit.py.
- schemas/auth.py; repositories/users.py.
- services/auth.py, services/profiles.py.
- api/dependencies.py; api/v1/auth.py, users.py, access.py.
- cli/__init__.py, cli/create_staff.py.
- tests/test_security.py, tests/test_auth_integration.py.
- scripts/start-api.ps1, scripts/stop-api.ps1.
- docs/authentication.md, docs/implementation-summary.md.

Modified: settings/main/router/package descriptions, requirements/example environment,
shared guarded DB test fixtures, PostgreSQL start helper, READMEs, architecture/setup
and progress docs. The source appendix in README includes every current source file.
New direct deps: pwdlib[argon2] 0.3.1, PyJWT 2.15.1, email-validator 2.3.0 with pinned
transitives. No unrelated libraries or schema/business feature was added.

## Verified results
- Phase 4 baseline: 32 passed before Phase 5.
- Full current suite --run-db: 80 passed, one upstream Starlette/AnyIO deprecation warning.
- Ordinary suite without --run-db: 41 passed, 39 intentionally skipped, same warning.
- Tests include actual runtime-role HTTP flows, all roles, deactivation, live role
  changes, unknown-user tokens, strict JWT cases, password hashing/rehashing,
  rate limits, rollback, concurrent signup, privacy and trusted staff CLI behavior.
- Database/migration checks: ready, UTC, 0001_initial; no drift; dependencies consistent.
- Development was not reset or seeded with demo/admin/test accounts by this work.
- All destructive DB test setup checks ACTUAL current_database()==dailydabba_test;
  refuses development/unknown tables; shared suite cleans up and downgrades test DB.
- Phases 1–4 are saved in commit 026128c (bckend base created), after initial
  scaffold ae4cd0e. Current Phase 5 changes remain uncommitted; no new commit was
  made in this turn. Credentials/runtime state/logs/dependencies/caches remain
  ignored or outside Git. Git identity was not changed.
- Docker is absent; its previously supplied path is not container-launch verified.

## Limits and decisions still pending
- Foundation is local, not production deployment. No refresh/revocation/logout
  endpoint, password-reset/change, email verification or MFA workflow yet.
- Role access checks are demonstrations; no operational admin/kitchen APIs yet.
- Process-local auth throttle is not distributed abuse protection. Review trusted
  proxies, shared limits, TLS, CORS and other production controls before exposure.
- Registration duplicate status reveals account existence; production policy needs review.
- Future order/credit/refund business guarantees are not implied by existing tables.
- Tax/delivery charges, service area, cancellation/refund rules, credit conversion,
  multi-account/partial restores, skip deadlines, pause extensions and deduction
  timing remain unapproved. Do not invent them in the address phase.

## Confirmation checklist and next phase
- [ ] Open http://127.0.0.1:8000/docs; health and readiness should work now.
- [ ] Register your own customer, login, Authorize with its token, retrieve/update /me.
- [ ] Confirm admin/kitchen access checks return 403 for that customer.
- [ ] Review implementation-summary.md for the full completed-work and remaining plan.
- [ ] Run --run-db if desired; expect 80 passed and the one known warning.
- [ ] Explicitly confirm Phase 5 before Phase 6.

Next (NOT STARTED): Phase 6 own-address create/list/update/soft-delete/default APIs,
with ownership checks and tests. Continue one phase at a time; no frontend work.
Do not edit already-applied 0001_initial, discard existing uncommitted work, reset
local development data or stop unrelated user processes when continuing.

Repository root package.json/package-lock.json and Swagger JavaScript dependencies
were observed and preserved as separate user work. They are not used by FastAPI.
Added only a root .gitignore to exclude node_modules and local environment secrets.
