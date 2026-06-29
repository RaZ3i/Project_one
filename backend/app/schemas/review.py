from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ReviewCreate(BaseModel):
    tutor_id: UUID
    lesson_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)

    @field_validator("comment")
    @classmethod
    def normalize_comment(cls, v: str | None) -> str | None:
        if v is not None and v.strip() == "":
            return None
        return v


class ReviewResponse(BaseModel):
    id: UUID
    student_id: UUID
    tutor_id: UUID
    lesson_id: UUID | None = None
    rating: int
    comment: str | None = None
    created_at: datetime
    student_name: str | None = None

    model_config = {"from_attributes": True}


class ReviewSummary(BaseModel):
    avg_rating: float | None = None
    review_count: int = 0
