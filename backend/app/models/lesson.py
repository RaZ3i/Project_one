import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class LessonStatus(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tutor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    slot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("availability_slots.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    status: Mapped[LessonStatus] = mapped_column(
        Enum(LessonStatus, name="lesson_status"), default=LessonStatus.scheduled, nullable=False
    )
    meeting_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped["User"] = relationship("User", back_populates="student_lessons", foreign_keys=[student_id])
    tutor: Mapped["User"] = relationship("User", back_populates="tutor_lessons", foreign_keys=[tutor_id])
    slot: Mapped["AvailabilitySlot"] = relationship("AvailabilitySlot", back_populates="lesson")


from app.models.user import User  # noqa: E402
from app.models.slot import AvailabilitySlot  # noqa: E402
