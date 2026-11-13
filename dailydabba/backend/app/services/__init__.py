"""Business use cases and transaction coordination.

Authentication and profile services own complete commits and call repositories.
Services do not depend on FastAPI route or HTTP request/response objects.
"""
