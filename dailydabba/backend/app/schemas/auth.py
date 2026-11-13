"""Authentication input/output contracts; passwords are write-only secrets."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    StringConstraints,
    model_validator,
)

Role = Literal["customer", "admin", "kitchen_staff"]
Name = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)
]
Phone = Annotated[str, StringConstraints(pattern=r"^\+[1-9][0-9]{7,14}$")]


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr = Field(max_length=254)
    password: SecretStr = Field(min_length=12, max_length=128)
    full_name: Name
    phone: Phone | None = None


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr = Field(max_length=254)
    password: SecretStr = Field(min_length=1, max_length=128)


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: Name | None = None
    phone: Phone | None = None

    @model_validator(mode="after")
    def valid_update(self) -> "ProfileUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide full_name or phone")
        if "full_name" in self.model_fields_set and self.full_name is None:
            raise ValueError("full_name cannot be null")
        return self


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    full_name: str
    phone: str | None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    role: Role
    is_active: bool
    created_at: datetime
    profile: ProfileResponse | None


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class AccessResponse(BaseModel):
    status: Literal["allowed"] = "allowed"
    role: Role
