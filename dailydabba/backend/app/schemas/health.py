"""The public health-response contract."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Keep the health response small and free of sensitive configuration."""

    status: Literal["ok"]


class ReadinessResponse(BaseModel):
    """Database connectivity/configuration and migration readiness contract."""

    status: Literal["ready"]
