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
