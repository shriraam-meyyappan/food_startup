# DailyDabba implementation summary and remaining plan

Updated: 13 November 2026, Asia/Kolkata. This document records actual implemented
work, verified behavior and remaining work through Phase 5. It is a technical
handoff for the four-person team, not a claim that the food business backend is
finished or deployed.

## Current result

The active Python backend is in `dailydabba/backend`. PostgreSQL 17.12 runs on
localhost port 55432. The API has been left running on localhost port 8000.
Open <http://127.0.0.1:8000/docs> to try the current operations.

- Phase 4 was checked and restored before starting Phase 5.
- All **80 tests pass**, with one known upstream test-library deprecation warning.
- Database readiness is ready, sessions use UTC, and Alembic reports no schema drift.
- The database has 23 application tables plus alembic_version at 0001_initial.
- Customer registration/login, self-profile access and all three roles are working.
- No frontend app, customer screen, dashboard, theme or branding was changed.
- No real payment provider, external notification service or deployment is connected.
- Phases 1–4 are saved in commit 026128c; current Phase 5 work is uncommitted for review.

## Initial monorepo setup (before numbered backend phases)

The existing repository and README/history were inspected and preserved. A
`dailydabba/` monorepo was created with independently runnable Next.js/TypeScript
web, Flutter/Dart Android and NestJS/TypeScript API starters, documentation,
PostgreSQL Compose infrastructure, environment examples, ignore rules and lockfiles.
The initial scaffold commit is `ae4cd0e` (`chore: initialize DailyDabba monorepo`).

The team then explicitly changed the active backend stack to Python, FastAPI,
SQLAlchemy and Alembic. That backend lives separately in `backend/`. The earlier
NestJS/Prisma starter remains historical work in services/api; do not run it as
the current backend. Both client entry points remain blank starter applications.
This explains why both Python and NestJS files exist without requiring a second
running backend or a microservice architecture.

## Phase 1 — Python backend initialization

Completed:

- Verified Python 3.13.5, satisfying the requested Python 3.12+ baseline.
- Created the isolated `.venv` and pinned tested Python dependencies.
- Added the FastAPI application factory and versioned GET /api/v1/health route.
- Added Pydantic environment settings, safe examples and ignored local .env.
- Added UTC console logging, automatic Swagger/OpenAPI documentation and six tests.
- Wrote exact installation/run commands and complete source listings.

Why it matters: the team gets a repeatable application that can start, validate
configuration and report that it can serve a request. Health returning only
`{"status":"ok"}` is intentional; it is not a page listing implementation progress.

Primary files: app/main.py, core/config.py, core/logging.py, api/v1/health.py,
schemas/health.py, tests, requirements and README.

## Phase 2 — Maintainable architecture

Completed:

- Centralized all version 1 routes in app/api/v1/router.py.
- Defined separate responsibilities for routes, schemas, models, services,
  repositories, database infrastructure, configuration and tests.
- Established package boundaries without inventing generic base services,
  microservices or a dependency-injection container.
- Explained request flow, dependency direction and transaction ownership.

Why it matters: a route handles HTTP and validation; a service coordinates a use
case; a repository issues database queries; a SQLAlchemy model describes storage.
Pydantic schemas describe public API data, including what must never be returned.
These responsibilities now have concrete implementations in Phase 5.

Reference: [architecture](architecture.md).

## Phase 3 — Database design and models

Completed 23 mapped tables, grouped by responsibility:

- Identity: users, customer_profiles, addresses.
- Food: food_categories, food_items, daily_menus, menu_items.
- Commerce: delivery_slots, carts, cart_items, orders, order_items.
- Subscriptions: subscription_plans, subscriptions, subscription_events,
  subscription_credits, credit_transactions.
- Payment evidence: payments, refunds, payment_webhook_events.
- Operations: kitchen_orders, notifications, audit_logs.

Key design decisions:

- UUID primary keys; timezone-aware event timestamps; Chennai-local business dates.
- Integer paise for money; no floating-point prices.
- Snapshot order prices, item names, addresses and delivery windows.
- Named primary/foreign/check/unique constraints and appropriate lookup indexes.
- Composite foreign keys preserve related ownership and dated meal selection.
- Partial unique indexes guard default addresses, skips and purchase credit grants.
- Credit ledger entries trace signed changes; a nonnegative cached balance is separate.
- Unique request/event/provider identifiers support later idempotent operations.
- Retain important history; only disposable cart items use cascading deletes.
- One current role per user is a constrained column rather than extra role/join tables.

A complete Mermaid ER diagram, column/constraint reference, review-only PostgreSQL
DDL and seven read-only SQL examples were written. An offline compiler verifies
that models can generate PostgreSQL definitions without creating a database.

Why it matters: business records have a consistent structure before APIs use them.
A table definition is not a working cart/order/payment feature. Cross-row totals,
state transitions, refund limits and concurrent credit redemption still require
future service transactions and reviewed policies.

Reference: [database design](database-design.md).

## Phase 4 — Real PostgreSQL and migrations

Completed:

- Installed official PostgreSQL 17.12 Windows binaries in the user's local app
  directory, outside the repository and OneDrive, without changing PATH or
  creating a Windows service.
- Configured localhost-only port 55432, SCRAM passwords and UTC sessions.
- Separated schema-owning migration credentials from limited application credentials.
- Added Psycopg 3, SQLAlchemy engine pooling/pre-ping/timeouts and scoped sessions.
- Added explicit local database/role provisioning and start/stop helpers.
- Added Alembic configuration, migration template and frozen initial migration.
- Applied initial migration 0001_initial to the development database.
- Verified upgrade -> downgrade -> upgrade and model/schema drift on a dedicated test DB.
- Added GET /api/v1/ready to check connection, UTC and current migration head.
- Added real PostgreSQL constraint, permission and request-rollback tests.
- Updated Docker initialization for separate admin/migration/runtime roles and test DB.

Runtime protection now includes no schema creation or Alembic-version mutation,
no update/delete on ledger/audit/event/item history, and narrow column updates on
orders, balances and payment lifecycle records. The runtime account does not own
the schema. Owners/superusers still have administrative control; services must
also enforce valid business operations and user-level authorization.

The application never automatically creates tables or migrates at startup.
Services own commits. Failed/uncommitted request work rolls back when its session
closes. Alembic is the schema history; the review-only schema.sql is not a migration.

### What was rechecked and repaired for this request

PostgreSQL was not running and recovered from an earlier interruption. Starting it encountered a
Windows log-file sharing delay during recovery because its startup log was inside
the data directory. Recovery completed and all original 32 tests passed. The
server was then cleanly restarted with logging outside the data directory, and
the start helper was given a 120-second recovery timeout.

No data directory was deleted/reinitialized, no database was reset for repair,
and no existing migration was edited. Live health/readiness were checked. The
PostgreSQL installation still does not auto-start after reboot: use the documented
start command/helper. Docker is not installed here, so its container launch remains
unverified; the native installation is the tested option on this machine.

Reference: [database setup](database-setup.md).

## Phase 5 — Authentication, users and roles

Completed operations:

1. POST /api/v1/auth/register: creates an active customer and private profile atomically.
2. POST /api/v1/auth/login: verifies password/status and issues a short-lived bearer JWT.
3. GET /api/v1/users/me: returns the authenticated user's account/profile only.
4. PATCH /api/v1/users/me/profile: updates only permitted own-profile fields.
5. GET /api/v1/admin/access-check: proves admin-only route protection.
6. GET /api/v1/kitchen/access-check: allows kitchen staff and admin, rejects customers.

The health/readiness routes remain available, giving eight current API paths.
Role-check endpoints are demonstrations, not operational admin/kitchen APIs.

Security and correctness implemented:

- Salted Argon2id hashing; no plaintext password storage or hash in API responses.
- Rehash older password parameters after successful verification when needed.
- Cryptographically generated signing secret stored only in ignored local .env.
- Fixed HS256 verification and required expiry/issue/not-before/issuer/audience/
  subject/JWT-ID/access-type claims; no role or password in the JWT.
- Database lookup on every protected request, so role changes and account
  deactivation are reflected without waiting for an old role claim to expire.
- Customers cannot choose a role during registration or profile updates.
- Anonymous/invalid credentials get 401; authenticated disallowed roles get 403.
- Case-normalized email uniqueness with PostgreSQL ON CONFLICT for concurrent registrations.
- User/profile/audit transaction boundaries; no orphan profiles on failures.
- Validation errors do not echo submitted inputs, and SQL errors are sanitized.
- Bounded process-local auth throttling with Retry-After and no-store API responses.
- Minimal audit events for registration, privileged account creation and profile changes.
- Staff accounts are created only through a trusted local CLI with hidden password prompts.
  It refuses existing emails instead of silently promoting or replacing an account.

Profile updates permit full_name and phone; phone may be cleared with null. They
cannot change email, password, account status, another user's ID or role.
Names and phone formats are validated, passwords must be 12–128 characters, and
unknown request fields are rejected.

The Phase 3 schema already had all needed fields, so Phase 5 required NO schema
migration. The applied revision remains 0001_initial. Role/authentication tests
used only the scratch database; no default privileged account or demo customer
was created in the development database.

Reference: [authentication guide](authentication.md), including Swagger,
PowerShell, staff initialization and complete request/response descriptions.

## Verification and how to reproduce

From the backend directory:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m app.db.check
.\.venv\Scripts\python.exe -m alembic check
.\.venv\Scripts\python.exe -m pytest -q --run-db
```

Expected: no broken requirements; ready/UTC/0001_initial; no new upgrade operations;
**80 passed** and one existing Starlette/AnyIO deprecated-alias warning.

Without --run-db: **41 passed, 39 skipped** and that same warning. Skips are
intentional because real-database checks require explicit permission to reset the
scratch dailydabba_test schema. Tests verify its actual connected database name,
refuse development/unknown tables, and clean up afterward. Never keep useful data
in that test database.

Coverage includes Phase 4's real constraints/permissions/migration rollback plus
JWT rejection cases, password salting/verification/upgrades, missing-secret behavior,
throttling, registration races and rollback, audit privacy, profile ownership,
forbidden field assignment, three roles, role changes, disabled users and staff CLI.
The full suite can take a minute or more because it deliberately hashes passwords.

## What is not complete

There are no functional address, menu-management, cart, checkout, subscription,
payment, kitchen-operation or reporting APIs yet. Their models are foundations.
No frontend has been designed or connected. No real customer data, payment keys,
notification credentials, recurring payment collection or deployment was added.

This is a locally verified foundation, not production-ready identity/deployment.
Email verification, password reset/change workflows, refresh/revocable sessions,
MFA policy, distributed abuse controls, reviewed proxy/CORS/TLS settings and
production operational recovery require further work. Signing-key rotation currently
invalidates all access tokens; there is no server-side per-token logout/revocation.
No claim is made that database constraints alone implement business correctness.

## Remaining phase-by-phase plan (not started)

- **Phase 6 — Addresses:** own-address CRUD, soft deletion and atomic default
  changes. Prove that users cannot read or modify another user's address.
- **Phase 7 — Food and menus:** admin-managed catalog/prices/dated menus and
  customer/public retrieval limited to active, available offerings.
- **Phase 8 — Cart:** add/update/remove/retrieve, server-calculated prices and
  charges, valid quantities and availability checks. Never trust client totals.
- **Phase 9 — Orders:** transactional/idempotent creation, item/address/time
  snapshots, order history, reviewed state transitions and cancellation rules.
- **Phase 10 — Subscriptions:** explicit purchased terms, credit grant/redemption
  protocol, balance reconciliation, skip/pause/renewal/expiry and concurrency tests.
  Agree the fulfillment deduction point and deadlines before implementing them.
- **Phase 11 — Payments:** test-mode Razorpay architecture, signed raw-body webhook
  verification, provider-event/payment deduplication, reconciliation and safe refunds.
  No automatic recurring collection in the initial version.
- **Phase 12 — Operations:** protected admin/kitchen endpoints, preparation counts,
  lifecycle updates and basic backend reports. No dashboards or frontend screens.
- **Phase 13 — Broader testing:** extend the existing suite to all business
  workflows, invalid/duplicate requests and payment/credit failure cases.
- **Phase 14 — Hardening:** review authorization, input limits, shared throttling,
  security/audit/privacy handling, backup strategy and production auth safeguards.
- **Phase 15 — Deployment preparation:** backend container/configuration, migration
  release process, logging/monitoring, backups and tested recovery instructions.
  Discuss configuration/security before any actual deployment.

One phase at a time remains the rule. Current authorization ends at Phase 5.
Read the authentication guide and confirm the register/login/profile flow before
starting Phase 6.

## Decisions still needed before affected business phases

The team has not finalized credit-to-meal conversion, combined credit accounts,
partial credit restorations, deduction timing, skip deadlines, pause extensions,
calendar-month terms, tax/delivery-charge values, cancellation/refund eligibility,
service-area validation and future multi-meal checkout needs. The current model
boundaries and policy snapshots do not silently choose those business policies.

Keep these decisions separate from UI/UX choices. Backend JSON contracts can be
reviewed now without choosing layouts, screens or branding. Within the four-person
team, split a confirmed feature by API/schema, persistence/migrations, service rules,
and tests/documentation, then review the entire transaction together.

## Git and handoff

The initial scaffold commit is ae4cd0e. Backend work through Phase 4 is saved in
026128c (bckend base created). Current Phase 5 changes and startup fixes remain
uncommitted and should be reviewed before committing. Environment files, signing/database secrets,
virtual environments, caches, data and runtime logs are ignored or outside Git.
No Git identity was changed. Separate root Swagger JavaScript package files were
left untouched; FastAPI does not use them for its automatic /docs. A root .gitignore
now excludes dependencies and local secrets from accidental staging. Do not overwrite an applied migration or discard
existing work when continuing in another chat.

For continuation read PROGRESS.md, this summary, authentication.md, database-setup.md,
then actual source. Complete code for every source/configuration file is included
in the backend README. The next authorized step requires Phase 5 confirmation.
