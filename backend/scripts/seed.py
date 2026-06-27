"""Заполнение демо-данными для платформы репетиторства."""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.database import async_session_maker
from app.core.security import get_password_hash
from app.models.lesson import Lesson, LessonStatus
from app.models.review import Review
from app.models.slot import AvailabilitySlot
from app.models.tutor_profile import TutorProfile
from app.models.user import User, UserGender, UserRole

TUTORS = [
    {
        "email": "anna.tutor@example.com",
        "full_name": "Анна Иванова",
        "gender": UserGender.female,
        "birth_year": 1988,
        "city": "Москва",
        "bio": "Опытный репетитор по математике с 10-летним стажем преподавания.",
        "subjects": "Математика, Алгебра, Геометрия",
        "meeting_url": "https://meet.google.com/abc-defg-hij",
    },
    {
        "email": "petr.tutor@example.com",
        "full_name": "Пётр Смирнов",
        "gender": UserGender.male,
        "birth_year": 1990,
        "city": "Санкт-Петербург",
        "bio": "Специалист по английскому языку и подготовке к ЕГЭ.",
        "subjects": "Английский язык",
        "meeting_url": "https://zoom.us/j/123456789",
    },
    {
        "email": "elena.tutor@example.com",
        "full_name": "Елена Козлова",
        "gender": UserGender.female,
        "birth_year": 1985,
        "city": "Казань",
        "bio": "Преподаватель физики, подготовка к ОГЭ и ЕГЭ.",
        "subjects": "Физика, Математика",
        "meeting_url": "https://meet.google.com/phys-elena",
    },
    {
        "email": "dmitry.tutor@example.com",
        "full_name": "Дмитрий Волков",
        "gender": UserGender.male,
        "birth_year": 1992,
        "city": "Новосибирск",
        "bio": "Химия и биология для школьников и студентов.",
        "subjects": "Химия, Биология",
        "meeting_url": "https://zoom.us/j/chem-dmitry",
    },
    {
        "email": "olga.tutor@example.com",
        "full_name": "Ольга Новикова",
        "gender": UserGender.female,
        "birth_year": 1987,
        "city": "Екатеринбург",
        "bio": "Русский язык и литература, помощь с сочинениями.",
        "subjects": "Русский язык, Литература",
        "meeting_url": "https://meet.google.com/rus-olga",
    },
    {
        "email": "sergey.tutor@example.com",
        "full_name": "Сергей Морозов",
        "gender": UserGender.male,
        "birth_year": 1983,
        "city": "Москва",
        "bio": "История и обществознание, подготовка к экзаменам.",
        "subjects": "История, Обществознание",
        "meeting_url": "https://zoom.us/j/hist-sergey",
    },
    {
        "email": "marina.tutor@example.com",
        "full_name": "Марина Соколова",
        "gender": UserGender.female,
        "birth_year": 1991,
        "city": "Краснодар",
        "bio": "Информатика и программирование для школьников.",
        "subjects": "Информатика",
        "meeting_url": "https://meet.google.com/it-marina",
    },
    {
        "email": "alex.tutor@example.com",
        "full_name": "Алексей Попов",
        "gender": UserGender.male,
        "birth_year": 1989,
        "city": "Воронеж",
        "bio": "География и биология, интерактивные уроки.",
        "subjects": "География, Биология",
        "meeting_url": "https://zoom.us/j/geo-alex",
    },
]

STUDENTS = [
    {"email": "student@example.com", "full_name": "Мария Петрова", "gender": UserGender.female, "birth_year": 2008, "city": "Москва"},
    {"email": "ivan.student@example.com", "full_name": "Иван Кузнецов", "gender": UserGender.male, "birth_year": 2009, "city": "Москва"},
    {"email": "sofia.student@example.com", "full_name": "София Лебедева", "gender": UserGender.female, "birth_year": 2007, "city": "Санкт-Петербург"},
    {"email": "artem.student@example.com", "full_name": "Артём Фёдоров", "gender": UserGender.male, "birth_year": 2010, "city": "Казань"},
    {"email": "daria.student@example.com", "full_name": "Дарья Орлова", "gender": UserGender.female, "birth_year": 2008, "city": "Новосибирск"},
    {"email": "nikita.student@example.com", "full_name": "Никита Белов", "gender": UserGender.male, "birth_year": 2009, "city": "Екатеринбург"},
]

REVIEWS_DATA = [
    (0, 0, 5, "Отличный репетитор! Объясняет понятно и терпеливо."),
    (1, 0, 4, "Хорошие занятия, заметный прогресс за месяц."),
    (2, 1, 5, "Помогла подготовиться к экзамену, рекомендую."),
    (3, 2, 4, "Интересные эксперименты на уроках физики."),
    (4, 3, 5, "Сдал химию на 5 благодаря Дмитрию."),
    (0, 4, 5, "Лучший репетитор по математике!"),
    (1, 5, 4, "Грамотный преподаватель истории."),
]


async def seed() -> None:
    async with async_session_maker() as db:
        existing = await db.execute(select(User).limit(1))
        if existing.scalar_one_or_none():
            print("Database already has data, skipping seed.")
            return

        password_hash = get_password_hash("password123")
        tutor_users: list[User] = []
        student_users: list[User] = []

        for t in TUTORS:
            user = User(
                id=uuid.uuid4(),
                email=t["email"],
                password_hash=password_hash,
                full_name=t["full_name"],
                role=UserRole.tutor,
                gender=t["gender"],
                birth_year=t["birth_year"],
                city=t["city"],
                phone="+7 900 000 00 01",
            )
            tutor_users.append(user)
            db.add(user)

        for s in STUDENTS:
            user = User(
                id=uuid.uuid4(),
                email=s["email"],
                password_hash=password_hash,
                full_name=s["full_name"],
                role=UserRole.student,
                gender=s["gender"],
                birth_year=s["birth_year"],
                city=s["city"],
            )
            student_users.append(user)
            db.add(user)

        await db.flush()

        for user, t in zip(tutor_users, TUTORS):
            db.add(
                TutorProfile(
                    user_id=user.id,
                    bio=t["bio"],
                    subjects=t["subjects"],
                    default_meeting_url=t["meeting_url"],
                )
            )

        base = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        slots: list[AvailabilitySlot] = []
        for i, tutor in enumerate(tutor_users):
            for day_offset in range(1, 4):
                slot = AvailabilitySlot(
                    tutor_id=tutor.id,
                    starts_at=base + timedelta(days=day_offset, hours=10 + i),
                    ends_at=base + timedelta(days=day_offset, hours=11 + i),
                )
                slots.append(slot)
                db.add(slot)

        await db.flush()

        completed_lessons: list[Lesson] = []
        for idx, (student_idx, tutor_idx, rating, comment) in enumerate(REVIEWS_DATA):
            slot = AvailabilitySlot(
                tutor_id=tutor_users[tutor_idx].id,
                starts_at=base - timedelta(days=30 - idx, hours=14),
                ends_at=base - timedelta(days=30 - idx, hours=15),
                is_booked=True,
            )
            db.add(slot)
            await db.flush()

            lesson = Lesson(
                student_id=student_users[student_idx].id,
                tutor_id=tutor_users[tutor_idx].id,
                slot_id=slot.id,
                status=LessonStatus.completed,
                meeting_url=TUTORS[tutor_idx]["meeting_url"],
            )
            db.add(lesson)
            await db.flush()
            completed_lessons.append(lesson)

            db.add(
                Review(
                    student_id=student_users[student_idx].id,
                    tutor_id=tutor_users[tutor_idx].id,
                    lesson_id=lesson.id,
                    rating=rating,
                    comment=comment,
                )
            )

        upcoming_slot = AvailabilitySlot(
            tutor_id=tutor_users[0].id,
            starts_at=base + timedelta(days=2, hours=10),
            ends_at=base + timedelta(days=2, hours=11),
            is_booked=True,
        )
        db.add(upcoming_slot)
        await db.flush()
        db.add(
            Lesson(
                student_id=student_users[0].id,
                tutor_id=tutor_users[0].id,
                slot_id=upcoming_slot.id,
                status=LessonStatus.scheduled,
                meeting_url=TUTORS[0]["meeting_url"],
            )
        )

        await db.commit()
        print("Seed complete.")
        print(f"  Tutors: {len(tutor_users)} accounts (password123)")
        print(f"  Students: {len(student_users)} accounts (password123)")
        print(f"  Reviews: {len(REVIEWS_DATA)}, completed lessons: {len(completed_lessons)}")
        print("  Demo student: student@example.com / password123")


if __name__ == "__main__":
    asyncio.run(seed())
