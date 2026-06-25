import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TutorProfile(Base):
    __tablename__ = "tutor_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    subjects: Mapped[str | None] = mapped_column(String(500), nullable=True)
    default_meeting_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="tutor_profile")


from app.models.user import User  # noqa: E402
