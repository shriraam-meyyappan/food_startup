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
