import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    student = "student"
    tutor = "tutor"


class UserGender(str, enum.Enum):
    male = "male"
    female = "female"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[UserGender | None] = mapped_column(Enum(UserGender, name="user_gender"), nullable=True)
    birth_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
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
    reviews_written: Mapped[list["Review"]] = relationship(
        "Review", back_populates="student", foreign_keys="Review.student_id"
    )
    reviews_received: Mapped[list["Review"]] = relationship(
        "Review", back_populates="tutor", foreign_keys="Review.tutor_id"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )


from app.models.tutor_profile import TutorProfile  # noqa: E402
from app.models.slot import AvailabilitySlot  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402
from app.models.review import Review  # noqa: E402
from app.models.notification import Notification  # noqa: E402
