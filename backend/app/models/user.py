import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    student = "student"
    tutor = "tutor"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tutor_profile: Mapped["TutorProfile | None"] = relationship(
        "TutorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    availability_slots: Mapped[list["AvailabilitySlot"]] = relationship(
        "AvailabilitySlot", back_populates="tutor", cascade="all, delete-orphan"
    )
    student_lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson", back_populates="student", foreign_keys="Lesson.student_id"
    )
    tutor_lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson", back_populates="tutor", foreign_keys="Lesson.tutor_id"
    )


from app.models.tutor_profile import TutorProfile  # noqa: E402
from app.models.slot import AvailabilitySlot  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
