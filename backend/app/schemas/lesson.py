from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.lesson import LessonStatus, LessonType


class LessonCreate(BaseModel):
    slot_id: UUID
    subject: str = Field(min_length=1, max_length=100)


class LessonUpdate(BaseModel):
    status: LessonStatus | None = None
    meeting_url: str | None = Field(default=None, max_length=500)
    recording_url: str | None = Field(default=None, max_length=500)
    notes: str | None = None

    @field_validator("meeting_url", "recording_url")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
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
    subject: str
    lesson_type: LessonType
    meeting_url: str | None
    recording_url: str | None
    effective_meeting_url: str | None = None
    notes: str | None
    created_at: datetime
    slot_starts_at: datetime | None = None
    slot_ends_at: datetime | None = None
    student_name: str | None = None
    tutor_name: str | None = None
    student_avatar_url: str | None = None
    tutor_avatar_url: str | None = None
    student_gender: str | None = None
    tutor_gender: str | None = None
    has_review: bool = False

    model_config = {"from_attributes": True}


class TutorBookingInfo(BaseModel):
    subjects: list[str]
    is_trial: bool
