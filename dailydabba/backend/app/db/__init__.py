"""Database engines, scoped sessions, checks and offline schema tools.

Table changes run only through explicit Alembic commands, never on import or
application startup. Provisioning is a separate, explicitly invoked admin tool.
"""
