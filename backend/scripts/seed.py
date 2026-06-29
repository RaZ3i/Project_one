"""Заполнение демо-данными для платформы репетиторства."""

import argparse
import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from app.core.database import async_session_maker
from app.core.security import get_password_hash
from app.core.subjects import parse_tutor_subjects
from app.models.lesson import Lesson, LessonStatus, LessonType
from app.models.notification import Notification, NotificationType
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

# (student_idx, tutor_idx, rating, comment) — one review per student-tutor pair
REVIEWS_DATA = [
    (0, 0, 5, "Отличный репетитор! Объясняет понятно и терпеливо."),
    (1, 0, 4, "Хорошие занятия, заметный прогресс за месяц."),
    (2, 1, 5, "Помогла подготовиться к экзамену, рекомендую."),
    (3, 2, 4, "Интересные эксперименты на уроках физики."),
    (4, 3, 5, "Сдал химию на 5 благодаря Дмитрию."),
    (0, 4, 5, "Помогла разобраться с сочинением, очень внимательная!"),
    (1, 5, 4, "Грамотный преподаватель истории."),
]

# Extra lessons without reviews: (student_idx, tutor_idx, status, days_offset, subject_idx, recording_url, cancellation_reason)
# days_offset: negative = past, positive = future
EXTRA_LESSONS_DATA = [
    # Мария + Анна: пробный (в REVIEWS) → регулярный завершённый → регулярный запланированный
    (0, 0, LessonStatus.completed, -14, 1, "https://www.youtube.com/watch?v=demo-maria-algebra", None),
    (0, 0, LessonStatus.scheduled, 2, 0, None, None),
    # София + Пётр: завершённый (в REVIEWS) → отменённый повторный
    (2, 1, LessonStatus.cancelled, -7, 0, None, "Репетитор заболел, перенесём на следующую неделю"),
    # Никита + Марина: завершённый пробный, отзыв ещё не оставлен
    (5, 6, LessonStatus.completed, -12, 0, "https://www.youtube.com/watch?v=demo-informatics", None),
    # Дарья + Алексей: пробный запланированный
    (4, 7, LessonStatus.scheduled, 4, 0, None, None),
    # Иван + Сергей: запланированный через 1 день (для напоминаний)
    (1, 5, LessonStatus.scheduled, 1, 0, None, None),
    # Артём + Елена: завершённый вчера (можно завершить/просмотреть)
    (3, 2, LessonStatus.completed, -1, 0, None, None),
]

DEMO_EMAILS = [t["email"] for t in TUTORS] + [s["email"] for s in STUDENTS]

RECORDING_URL_DEMO = "https://www.youtube.com/watch?v=demo123"


def tutor_subject(tutor_idx: int, subject_idx: int = 0) -> str:
    subjects = parse_tutor_subjects(TUTORS[tutor_idx]["subjects"])
    if not subjects:
        return "Математика"
    return subjects[min(subject_idx, len(subjects) - 1)]


def lesson_type_for_pair(
    pair: tuple[uuid.UUID, uuid.UUID], pairs_seen: set[tuple[uuid.UUID, uuid.UUID]]
) -> LessonType:
    lesson_type = LessonType.regular if pair in pairs_seen else LessonType.trial
    pairs_seen.add(pair)
    return lesson_type


async def add_lesson(
    db,
    *,
    student_users: list[User],
    tutor_users: list[User],
    base: datetime,
    student_idx: int,
    tutor_idx: int,
    status: LessonStatus,
    days_offset: int,
    subject_idx: int,
    recording_url: str | None,
    pairs_seen: set[tuple[uuid.UUID, uuid.UUID]],
    hour: int = 14,
    cancellation_reason: str | None = None,
) -> Lesson:
    pair = (student_users[student_idx].id, tutor_users[tutor_idx].id)
    lesson_type = lesson_type_for_pair(pair, pairs_seen)
    slot_booked = status in (LessonStatus.scheduled, LessonStatus.completed)

    slot = AvailabilitySlot(
        tutor_id=tutor_users[tutor_idx].id,
        starts_at=base + timedelta(days=days_offset, hours=hour),
        ends_at=base + timedelta(days=days_offset, hours=hour + 1),
        is_booked=slot_booked,
    )
    db.add(slot)
    await db.flush()

    lesson = Lesson(
        student_id=student_users[student_idx].id,
        tutor_id=tutor_users[tutor_idx].id,
        slot_id=slot.id,
        status=status,
        subject=tutor_subject(tutor_idx, subject_idx),
        lesson_type=lesson_type,
        meeting_url=TUTORS[tutor_idx]["meeting_url"],
        recording_url=recording_url if status == LessonStatus.completed else None,
        cancellation_reason=cancellation_reason if status == LessonStatus.cancelled else None,
    )
    db.add(lesson)
    await db.flush()
    return lesson


async def _lessons_for_student(db, student_id: uuid.UUID) -> list[Lesson]:
    result = await db.execute(select(Lesson).where(Lesson.student_id == student_id))
    return list(result.scalars().all())


async def clear_demo_data(db) -> int:
    result = await db.execute(select(User).where(User.email.in_(DEMO_EMAILS)))
    users = result.scalars().all()
    if not users:
        return 0

    user_ids = [u.id for u in users]
    await db.execute(
        delete(Notification).where(Notification.user_id.in_(user_ids))
    )
    await db.execute(
        delete(Review).where(
            (Review.student_id.in_(user_ids)) | (Review.tutor_id.in_(user_ids))
        )
    )
    await db.execute(
        delete(Lesson).where(
            (Lesson.student_id.in_(user_ids)) | (Lesson.tutor_id.in_(user_ids))
        )
    )
    await db.execute(delete(AvailabilitySlot).where(AvailabilitySlot.tutor_id.in_(user_ids)))
    await db.execute(delete(TutorProfile).where(TutorProfile.user_id.in_(user_ids)))
    await db.execute(delete(User).where(User.email.in_(DEMO_EMAILS)))
    await db.flush()
    return len(users)


FORCE_HINT = "python3 -m scripts.seed --force"


async def seed(force: bool = False) -> None:
    async with async_session_maker() as db:
        if force:
            cleared = await clear_demo_data(db)
            if cleared:
                print(f"Cleared {cleared} demo user(s) and related data.")
            await db.commit()
        else:
            demo_existing = await db.execute(
                select(User).where(User.email.in_(DEMO_EMAILS)).limit(1)
            )
            if demo_existing.scalar_one_or_none():
                print("Demo data already exists, skipping seed.")
                print(f"Re-seed with: {FORCE_HINT}")
                return
            existing = await db.execute(select(User).limit(1))
            if existing.scalar_one_or_none():
                print("Database already has data, skipping seed.")
                print(f"Re-seed demo data with: {FORCE_HINT}")
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
        for i, tutor in enumerate(tutor_users):
            for day_offset in range(1, 4):
                db.add(
                    AvailabilitySlot(
                        tutor_id=tutor.id,
                        starts_at=base + timedelta(days=day_offset, hours=10 + i),
                        ends_at=base + timedelta(days=day_offset, hours=11 + i),
                    )
                )

        await db.flush()

        pairs_seen: set[tuple[uuid.UUID, uuid.UUID]] = set()
        completed_count = 0
        scheduled_count = 0
        cancelled_count = 0

        for idx, (student_idx, tutor_idx, rating, comment) in enumerate(REVIEWS_DATA):
            lesson = await add_lesson(
                db,
                student_users=student_users,
                tutor_users=tutor_users,
                base=base,
                student_idx=student_idx,
                tutor_idx=tutor_idx,
                status=LessonStatus.completed,
                days_offset=-(30 - idx),
                subject_idx=0,
                recording_url=RECORDING_URL_DEMO if idx % 2 == 0 else None,
                pairs_seen=pairs_seen,
            )
            completed_count += 1

            db.add(
                Review(
                    student_id=student_users[student_idx].id,
                    tutor_id=tutor_users[tutor_idx].id,
                    lesson_id=lesson.id,
                    rating=rating,
                    comment=comment,
                )
            )

        for student_idx, tutor_idx, status, days_offset, subject_idx, recording_url, cancellation_reason in EXTRA_LESSONS_DATA:
            await add_lesson(
                db,
                student_users=student_users,
                tutor_users=tutor_users,
                base=base,
                student_idx=student_idx,
                tutor_idx=tutor_idx,
                status=status,
                days_offset=days_offset,
                subject_idx=subject_idx,
                recording_url=recording_url,
                pairs_seen=pairs_seen,
                hour=10 if status == LessonStatus.scheduled else 14,
                cancellation_reason=cancellation_reason,
            )
            if status == LessonStatus.completed:
                completed_count += 1
            elif status == LessonStatus.scheduled:
                scheduled_count += 1
            elif status == LessonStatus.cancelled:
                cancelled_count += 1

        # Demo notifications for main student account
        maria = student_users[0]
        anna = tutor_users[0]
        upcoming_lesson = next(
            (l for l in await _lessons_for_student(db, maria.id) if l.status == LessonStatus.scheduled),
            None,
        )
        db.add(
            Notification(
                user_id=maria.id,
                type=NotificationType.lesson_reminder,
                title="Напоминание о занятии",
                message=f"Завтра занятие по математике с {anna.full_name}. Не забудьте подготовиться!",
                read=False,
                related_lesson_id=upcoming_lesson.id if upcoming_lesson else None,
            )
        )
        db.add(
            Notification(
                user_id=maria.id,
                type=NotificationType.lesson_completed,
                title="Занятие завершено",
                message=f"Репетитор {anna.full_name} отметил занятие по алгебре как завершённое.",
                read=True,
            )
        )
        db.add(
            Notification(
                user_id=anna.id,
                type=NotificationType.lesson_booked,
                title="Новая запись на занятие",
                message=f"Ученик {maria.full_name} записался на повторное занятие.",
                read=False,
                related_lesson_id=upcoming_lesson.id if upcoming_lesson else None,
            )
        )

        await db.commit()
        total_lessons = completed_count + scheduled_count + cancelled_count
        print("Seed complete.")
        print(f"  Tutors: {len(tutor_users)} accounts (password123)")
        print(f"  Students: {len(student_users)} accounts (password123)")
        print(f"  Lessons: {total_lessons} ({completed_count} completed, {scheduled_count} scheduled, {cancelled_count} cancelled)")
        print(f"  Reviews: {len(REVIEWS_DATA)} (unique student-tutor pairs)")
        print("  Demo student: student@example.com / password123")
        print("    → trial + review with Анна, regular completed, regular scheduled upcoming")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed TutorHub demo data")
    parser.add_argument(
        "--force",
        action="store_true",
        help=f"Delete demo users (by email) and re-seed ({FORCE_HINT})",
    )
    args = parser.parse_args()
    asyncio.run(seed(force=args.force))
