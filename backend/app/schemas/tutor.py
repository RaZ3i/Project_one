from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TutorProfileUpdate(BaseModel):
    bio: str | None = None
    subjects: str | None = Field(default=None, max_length=500)
    default_meeting_url: str | None = Field(default=None, max_length=500)

    @field_validator("default_meeting_url")
    @classmethod
    def validate_meeting_url(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL должен начинаться с http:// или https://")
        return v


class TutorListItem(BaseModel):
    id: UUID
    full_name: str
    subjects: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    avg_rating: float | None = None
    review_count: int = 0

    model_config = {"from_attributes": True}


class TutorDetail(BaseModel):
    id: UUID
    full_name: str
    email: str
    subjects: str | None = None
    bio: str | None = None
    default_meeting_url: str | None = None
    avatar_url: str | None = None
    avg_rating: float | None = None
    review_count: int = 0

    model_config = {"from_attributes": True}
