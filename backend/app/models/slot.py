import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tutor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_booked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    tutor: Mapped["User"] = relationship("User", back_populates="availability_slots")
    lesson: Mapped["Lesson | None"] = relationship("Lesson", back_populates="slot", uselist=False)


from app.models.user import User  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
