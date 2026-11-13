# Phase 5: Authentication, profiles and role access

Phase 4 was rechecked on 13 November 2026 before authentication work. PostgreSQL
was not running and recovered from an earlier interruption; it was started safely, migrations were
checked, and the original 32 tests passed. Startup logging was moved outside the
PostgreSQL data directory after a Windows sharing conflict delayed recovery. No
database was reinitialized, and development data was not reset.

Phase 5 is now implemented. Full verification: **80 passed, 1 known warning**.
No schema migration was needed: the Phase 3 user/profile schema already supports
these features. PostgreSQL remains at `0001_initial` with 23 application tables.

## Open the running backend

The verified local API has been started at <http://127.0.0.1:8000/docs>.

- `/api/v1/health` returns `{"status":"ok"}`.
- `/api/v1/ready` returns `{"status":"ready"}` when PostgreSQL and migrations are ready.
- `/docs` contains the registration, login, current-user and role-check operations.

These are API operations, not customer-facing pages. Both frontend apps remain
untouched. Do not start a second server on the same port while this one is running.

From `C:/Users/rmshr/OneDrive/Desktop/food_startup/dailydabba/backend`, the Windows
managed helpers are:

```powershell
.\scripts\start-api.ps1
.\scripts\stop-api.ps1
```

The start helper refuses to replace an unrelated listener, starts a hidden local
process without auto-reload, and records its process identity/log paths in ignored
`.local/api.process.json`. The stop helper verifies both the start timestamp and
workspace command before stopping only that API process tree. It does not stop
PostgreSQL. The API does not automatically restart after a machine reboot.

For interactive development instead, stop the managed API and run:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --no-proxy-headers
```

Then Ctrl+C stops that terminal's server. After reboot, also start PostgreSQL using
the commands in [database setup](database-setup.md). If PowerShell scripts are
blocked, use the direct executable commands documented there and the interactive
Uvicorn command above; changing execution policy is not needed for Python.

## Authentication configuration

The backend's existing ignored `.env` now has a generated persistent JWT signing
secret. The real key was not printed. Do not overwrite `.env` with the example.

Safe `.env.example` lists:

```dotenv
JWT_SECRET=replace_with_a_random_secret_before_starting
JWT_ISSUER=dailydabba-api
JWT_AUDIENCE=dailydabba-clients
ACCESS_TOKEN_MINUTES=15
AUTH_RATE_LIMIT_PER_MINUTE=10
```

The placeholder key is intentionally rejected. For a FRESH setup only, after
copying `.env.example`, generate a new key directly into the local file without
printing it:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; from dotenv import set_key; set_key('.env', 'JWT_SECRET', secrets.token_urlsafe(64))"
```

Do not regenerate it every start: changing the key invalidates existing tokens.
Use a cryptographically random secret, not a repeated or guessable 32-character
word. Settings require at least 32 encoded bytes and reject the example prefix.
Issuer/audience are configured identifiers. Token lifetime defaults to 15 minutes
and can be configured from 1 to 60 minutes. Missing signing configuration makes
authenticated token operations fail closed with 503; health remains separate.

Dependencies are pinned in requirements.txt: pwdlib with Argon2 support, PyJWT,
and Pydantic's email validator. Password hashes and JWT secrets are never returned
by user/profile schemas. Access tokens themselves are sensitive credentials and
are intentionally returned only by successful login.

## Endpoint contracts

### POST /api/v1/auth/register

JSON fields: `email`, `password`, `full_name`, optional `phone`.
Email must be valid and is stored lowercase. Full name is trimmed, nonempty and
at most 120 characters. Password is 12–128 characters; spaces inside a password
are preserved. Optional phone uses international format such as `+919876543210`.

The server always creates role `customer` with an active account. It rejects
client-supplied `role`, `is_active`, `id`, `password_hash`, or unknown fields.
A unique email conflict returns 409, including simultaneous requests. Success is
201 with `id`, `email`, `role`, `is_active`, `created_at` and `profile` (name/phone).
No password or password hash appears. Registration does not log the user in.

User, profile and minimal audit record are committed together. Password hashing
occurs before opening the write transaction. PostgreSQL ON CONFLICT handles
concurrent duplicate emails without leaving orphaned profiles or duplicate users.

### POST /api/v1/auth/login

JSON fields: `email`, `password`. This is a JSON endpoint, not an OAuth password
grant/form endpoint. Success returns HTTP 200:

```json
{"access_token":"<sensitive signed JWT>","token_type":"bearer","expires_in":900}
```

No real token is embedded in this guide. Unknown email, wrong password or inactive/
deactivated account all return the same 401 response with WWW-Authenticate: Bearer.
A dummy Argon2 verification mitigates an obvious unknown-account timing difference;
this is not a claim of perfectly constant end-to-end request timing. Successful
login upgrades older Argon2 hash parameters when needed.

Tokens are signed with fixed HS256 and verified with a fixed algorithm allowlist.
Required claims are subject UUID, issuer, audience, issue/not-before/expiry times,
JWT ID and access-token type. Missing/expired/future/wrong-issuer/wrong-audience/
wrong-signature/wrong-algorithm tokens are rejected. JWT contents are signed,
not encrypted; no password, email or role is placed in the token.

### GET /api/v1/users/me

Send `Authorization: Bearer <access_token>`. Returns the current user's account
and profile fields. The user ID comes from the verified JWT, not a query/body ID.
The account is fetched from PostgreSQL on every protected request; nonexistent,
inactive or deactivated users get 401 even with an otherwise valid signed token.

### PATCH /api/v1/users/me/profile

Send the bearer header plus JSON containing `full_name` and/or `phone`.
Omitted fields stay unchanged. `phone: null` clears the phone. `full_name: null`,
an empty update or unknown fields are rejected with 422. Email, password, account
status and roles are not editable through this endpoint.

Only the authenticated profile is changed. If an older account has no profile,
full_name is required to create one. The service commits the profile and a minimal
audit event together; audit details contain field names, not private values.
Email changes/password changes need separate reviewed verification flows, which
are not silently included here.

### GET /api/v1/admin/access-check

Admin role only: 200 `{"status":"allowed","role":"admin"}`.
Customers and kitchen staff receive 403. Anonymous requests receive 401.

### GET /api/v1/kitchen/access-check

Kitchen staff and admins receive 200 with their current role. Customers receive
403; anonymous requests receive 401. These small endpoints prove role protection;
they do not implement kitchen/admin operations or any dashboard.

Roles come from the current database account, not from client input or token role
claims. A role change applies on the next protected request without issuing a new
token. Admins being allowed into the kitchen access-check is an explicit current
policy, not a general bypass for every future operation.

## Try the complete flow in Swagger

1. Open `/docs`. Expand registration, choose Try it out, and supply your own valid
   email, full name and a private password of 12–128 characters. Do not use the
   example placeholder as a real password. Execute; expect 201 and role customer.
2. Expand login and supply the same email/password. Expect 200 with an access token.
3. Copy only the token value, choose Swagger's Authorize button, and paste it into
   the HTTPBearer field. Swagger adds the Bearer prefix; do not add it twice.
4. Execute GET /users/me. Expect your account/profile and no password/hash fields.
5. Execute PATCH /users/me/profile with a new full_name or phone. Confirm GET /me
   shows the update. No other account is addressed by these self-service routes.
6. Call the admin/kitchen access-check endpoints as that customer. Expect 403,
   which demonstrates authorization is working.

Do not share screenshots containing passwords or access tokens. All testing here
is localhost HTTP; use HTTPS before exposing authentication outside local work.

## PowerShell alternative without putting a password in command history

From the backend directory, prompt for your own values:

```powershell
$email = Read-Host 'Your email'
$name = Read-Host 'Your full name'
$secure = Read-Host 'Your password (12–128 characters)' -AsSecureString
$password = [pscredential]::new('unused', $secure).GetNetworkCredential().Password
$registerBody = @{ email = $email; password = $password; full_name = $name } | ConvertTo-Json
$account = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/auth/register -ContentType application/json -Body $registerBody
$loginBody = @{ email = $email; password = $password } | ConvertTo-Json
$token = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/auth/login -ContentType application/json -Body $loginBody
$headers = @{ Authorization = 'Bearer ' + $token.access_token }
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/v1/users/me -Headers $headers
Remove-Variable password, registerBody, loginBody, token, headers, secure
```

If already registered, skip registration and run the login portion. Postman or
Bruno can send the same JSON and bearer header; no client-specific integration is
required. An expired token requires another login.

## Create privileged accounts locally

There are no default admin credentials and no public role-assignment API. A trusted
operator with migration credentials can create a new staff account:

```powershell
$staffEmail = Read-Host 'Staff email'
$staffName = Read-Host 'Staff full name'
.\.venv\Scripts\python.exe -m app.cli.create_staff --email $staffEmail --full-name $staffName --role admin
```

For kitchen staff, choose `--role kitchen_staff`. The command prompts for the
password twice without echoing it. Do not put passwords in CLI arguments. It
creates the user/profile/audit atomically and refuses an existing email rather
than silently changing an existing role. Log in normally to obtain a token and
exercise the role checks. No privileged account was automatically created in the
development database by this implementation; role tests use the scratch database.

## Safeguards, errors and current limits

- Password hashing uses salted Argon2id; plaintext is never stored in the database.
- Typed schemas reject mass assignment. Response schemas select public fields.
- Validation errors omit submitted input/context values, avoiding password echoes.
- Invalid credentials return 401; authenticated-but-disallowed roles return 403.
  Duplicate email is 409, invalid input 422, throttling 429, unavailable auth/DB 503.
- Auth endpoints have a bounded, thread-safe, in-process sliding-minute throttle
  per client address and endpoint (default 10 requests/minute). 429 includes
  Retry-After. Local helpers disable proxy-header interpretation. Before a proxy
  deployment, configure trusted proxy handling and shared/gateway rate limiting;
  process-local limits reset on restart and are not a distributed abuse defense.
- API responses use Cache-Control: no-store. SQL errors are sanitized. Application code does not log request bodies,
  authorization headers, SQL parameters or full settings. Do not put secrets in
  URLs because HTTP access logs can include query strings.
- Duplicate registration status reveals whether an email exists; email ownership
  verification and registration-enumeration policy require a production decision.
- No refresh tokens, immediate per-token revocation/logout, password reset, email
  verification or MFA is implemented. Tokens expire after their configured TTL;
  account deactivation blocks subsequent requests immediately. Discarding a token
  is a client action, not server-side revocation. Rotating the signing key invalidates
  all previously issued tokens. Do not describe this local foundation as a complete
  production identity platform.
- No address, cart, order, subscription or payment APIs were added in Phase 5.
  Their tables exist, but operational behavior remains future phase work.

## Checks and sources

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -q --run-db
.\.venv\Scripts\python.exe -m alembic check
```

Expected ordinary run: 41 passed, 39 skipped. Full opt-in run: 80 passed.
One existing upstream Starlette/AnyIO test-library deprecation warning remains.
--run-db resets only the guarded dailydabba_test scratch database; do not keep useful
data there. Development data and the applied migration remain intact.

New tests cover password salting/verification/rehashing, strict JWT validation,
secret/error masking, throttling, registration races/rollback, profile ownership,
forbidden field assignment, all roles, live database role/status changes, audit
privacy and the staff CLI's duplicate-account safeguard.

Primary references: [FastAPI password hashing/JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
and [PyJWT verification API](https://pyjwt.readthedocs.io/en/stable/api.html).
The detailed completed-work and next-phase plan is in
[implementation summary](implementation-summary.md). Stop here until Phase 5 is
confirmed; Phase 6 will add address management.

FastAPI generates /docs automatically. JavaScript swagger-jsdoc/swagger-ui-express
packages at the repository root are separate user work and are not required by or
used for this Python backend. They were left untouched.
