"""SQLAlchemy queries and persistence operations, starting with user accounts.

Repositories receive a session from their caller. They make no HTTP decisions
and never independently commit a service transaction.
"""
