from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.user import UserGender, UserRole


class UserProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    gender: UserGender | None = None
    birth_year: int | None = Field(default=None, ge=1900, le=2100)
    phone: str | None = Field(default=None, max_length=50)
    city: str | None = Field(default=None, max_length=255)

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str | None) -> str | None:
        if v is not None and v.strip() == "":
            return None
        return v

    @field_validator("city")
    @classmethod
    def normalize_city(cls, v: str | None) -> str | None:
        if v is not None and v.strip() == "":
            return None
        return v


class UserProfileResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: UserRole
    gender: UserGender | None = None
    birth_year: int | None = None
    avatar_url: str | None = None
    phone: str | None = None
    city: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AvatarUploadResponse(BaseModel):
    avatar_url: str
