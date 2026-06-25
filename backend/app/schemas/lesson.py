from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.lesson import LessonStatus


class LessonCreate(BaseModel):
    slot_id: UUID


class LessonUpdate(BaseModel):
    status: LessonStatus | None = None
    meeting_url: str | None = Field(default=None, max_length=500)
    notes: str | None = None

    @field_validator("meeting_url")
    @classmethod
    def validate_meeting_url(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL должен начинаться с http:// или https://")
        return v


class LessonResponse(BaseModel):
    id: UUID
    student_id: UUID
    tutor_id: UUID
    slot_id: UUID
    status: LessonStatus
    meeting_url: str | None
    effective_meeting_url: str | None = None
    notes: str | None
    created_at: datetime
    slot_starts_at: datetime | None = None
    slot_ends_at: datetime | None = None
    student_name: str | None = None
    tutor_name: str | None = None

    model_config = {"from_attributes": True}
