"""Database tests are opt-in and may reset ONLY the dedicated test database."""

import pytest


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
