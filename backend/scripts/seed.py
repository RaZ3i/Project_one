"""Заполнение демо-данными для платформы репетиторства."""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.database import async_session_maker
from app.core.security import get_password_hash
from app.models.slot import AvailabilitySlot
from app.models.tutor_profile import TutorProfile
from app.models.user import User, UserRole


async def seed() -> None:
    async with async_session_maker() as db:
        existing = await db.execute(select(User).limit(1))
        if existing.scalar_one_or_none():
            print("Database already has data, skipping seed.")
            return

        tutor1 = User(
            id=uuid.uuid4(),
            email="anna.tutor@example.com",
            password_hash=get_password_hash("password123"),
            full_name="Anna Ivanova",
            role=UserRole.tutor,
        )
        tutor2 = User(
            id=uuid.uuid4(),
            email="petr.tutor@example.com",
            password_hash=get_password_hash("password123"),
            full_name="Petr Smirnov",
            role=UserRole.tutor,
        )
        student = User(
            id=uuid.uuid4(),
            email="student@example.com",
            password_hash=get_password_hash("password123"),
            full_name="Maria Student",
            role=UserRole.student,
        )

        db.add_all([tutor1, tutor2, student])
        await db.flush()

        db.add_all(
            [
                TutorProfile(
                    user_id=tutor1.id,
                    bio="Experienced math tutor with 10 years of teaching.",
                    subjects="Mathematics, Physics",
                    default_meeting_url="https://meet.google.com/abc-defg-hij",
                ),
                TutorProfile(
                    user_id=tutor2.id,
                    bio="English and IELTS preparation specialist.",
                    subjects="English, IELTS",
                    default_meeting_url="https://zoom.us/j/123456789",
                ),
            ]
        )

        base = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0) + timedelta(days=1)
        slots = [
            AvailabilitySlot(
                tutor_id=tutor1.id,
                starts_at=base + timedelta(hours=10),
                ends_at=base + timedelta(hours=11),
            ),
            AvailabilitySlot(
                tutor_id=tutor1.id,
                starts_at=base + timedelta(days=1, hours=14),
                ends_at=base + timedelta(days=1, hours=15),
            ),
            AvailabilitySlot(
                tutor_id=tutor2.id,
                starts_at=base + timedelta(hours=16),
                ends_at=base + timedelta(hours=17),
            ),
        ]
        db.add_all(slots)
        await db.commit()
        print("Seed complete.")
        print("  Tutors: anna.tutor@example.com, petr.tutor@example.com")
        print("  Student: student@example.com")
        print("  Password for all: password123")


if __name__ == "__main__":
    asyncio.run(seed())
