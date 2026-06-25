from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SlotCreate(BaseModel):
    starts_at: datetime
    ends_at: datetime

    @field_validator("ends_at")
    @classmethod
    def ends_after_starts(cls, ends_at: datetime, info) -> datetime:
        starts_at = info.data.get("starts_at")
        if starts_at and ends_at <= starts_at:
            raise ValueError("ends_at must be after starts_at")
        return ends_at


class SlotResponse(BaseModel):
    id: UUID
    tutor_id: UUID
    starts_at: datetime
    ends_at: datetime
    is_booked: bool

    model_config = {"from_attributes": True}
