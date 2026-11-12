"""Future SQLAlchemy queries and persistence operations.

Repositories will receive a database session from their caller. They must not
make HTTP decisions or commit a service's transaction independently.
"""
