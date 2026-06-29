from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.subjects import subject_allowed_for_tutor
from app.models.lesson import Lesson, LessonStatus, LessonType
from app.models.notification import NotificationType
from app.models.review import Review
from app.models.slot import AvailabilitySlot
from app.models.tutor_profile import TutorProfile
from app.models.user import User, UserRole
from app.schemas.lesson import LessonResponse
from app.services.notifications import create_notification


def get_effective_meeting_url(lesson: Lesson) -> str | None:
    if lesson.meeting_url:
        return lesson.meeting_url
    if lesson.tutor and lesson.tutor.tutor_profile:
        return lesson.tutor.tutor_profile.default_meeting_url
    return None


def lesson_to_response(lesson: Lesson, *, has_review: bool = False) -> LessonResponse:
    slot = lesson.slot
    return LessonResponse(
        id=lesson.id,
        student_id=lesson.student_id,
        tutor_id=lesson.tutor_id,
        slot_id=lesson.slot_id,
        status=lesson.status,
        subject=lesson.subject,
        lesson_type=lesson.lesson_type,
        meeting_url=lesson.meeting_url,
        recording_url=lesson.recording_url,
        effective_meeting_url=get_effective_meeting_url(lesson),
        notes=lesson.notes,
        cancellation_reason=lesson.cancellation_reason,
        created_at=lesson.created_at,
        slot_starts_at=slot.starts_at if slot else None,
        slot_ends_at=slot.ends_at if slot else None,
        student_name=lesson.student.full_name if lesson.student else None,
        tutor_name=lesson.tutor.full_name if lesson.tutor else None,
        student_avatar_url=lesson.student.avatar_url if lesson.student else None,
        tutor_avatar_url=lesson.tutor.avatar_url if lesson.tutor else None,
        student_gender=lesson.student.gender.value if lesson.student and lesson.student.gender else None,
        tutor_gender=lesson.tutor.gender.value if lesson.tutor and lesson.tutor.gender else None,
        has_review=has_review,
    )


def slot_is_actively_booked(slot: AvailabilitySlot) -> bool:
    """A slot is booked only when it has a scheduled (non-cancelled) lesson."""
    if slot.lesson is not None:
        return slot.lesson.status == LessonStatus.scheduled
    return slot.is_booked


async def release_slot(db: AsyncSession, slot_id: UUID) -> None:
    result = await db.execute(select(AvailabilitySlot).where(AvailabilitySlot.id == slot_id))
    slot = result.scalar_one_or_none()
    if slot is not None:
        slot.is_booked = False


def lesson_end_time(lesson: Lesson) -> datetime | None:
    if lesson.slot is None:
        return None
    return lesson.slot.ends_at or lesson.slot.starts_at


def lesson_has_ended(lesson: Lesson, *, now: datetime | None = None) -> bool:
    end = lesson_end_time(lesson)
    if end is None:
        return False
    current = now or datetime.now(timezone.utc)
    return end <= current


async def cancel_lesson_booking(
    db: AsyncSession,
    lesson: Lesson,
    *,
    cancellation_reason: str | None = None,
    cancelled_by: User | None = None,
) -> None:
    lesson.status = LessonStatus.cancelled
    if cancellation_reason:
        lesson.cancellation_reason = cancellation_reason
    await release_slot(db, lesson.slot_id)

    if cancelled_by is None:
        return

    slot = lesson.slot
    time_str = ""
    if slot and slot.starts_at:
        time_str = slot.starts_at.strftime("%d.%m.%Y %H:%M")

    if cancelled_by.role == UserRole.tutor and lesson.student:
        reason_text = f" Причина: {cancellation_reason}" if cancellation_reason else ""
        await create_notification(
            db,
            user_id=lesson.student_id,
            type=NotificationType.lesson_cancelled,
            title="Занятие отменено",
            message=f"Репетитор {cancelled_by.full_name} отменил занятие по предмету «{lesson.subject}»{f' ({time_str})' if time_str else ''}.{reason_text}",
            related_lesson_id=lesson.id,
        )
    elif cancelled_by.role == UserRole.student and lesson.tutor:
        await create_notification(
            db,
            user_id=lesson.tutor_id,
            type=NotificationType.lesson_cancelled,
            title="Занятие отменено учеником",
            message=f"Ученик {cancelled_by.full_name} отменил занятие по предмету «{lesson.subject}»{f' ({time_str})' if time_str else ''}.",
            related_lesson_id=lesson.id,
        )


async def student_has_prior_lessons_with_tutor(
    db: AsyncSession, student_id: UUID, tutor_id: UUID
) -> bool:
    result = await db.execute(
        select(
            exists(
                select(Lesson.id).where(
                    Lesson.student_id == student_id,
                    Lesson.tutor_id == tutor_id,
                    Lesson.status.in_([LessonStatus.scheduled, LessonStatus.completed]),
                )
            )
        )
    )
    return bool(result.scalar())


async def resolve_lesson_type(
    db: AsyncSession, student_id: UUID, tutor_id: UUID
) -> LessonType:
    has_prior = await student_has_prior_lessons_with_tutor(db, student_id, tutor_id)
    return lesson_type_from_prior(has_prior)


def lesson_type_from_prior(has_prior: bool) -> LessonType:
    return LessonType.regular if has_prior else LessonType.trial


async def lesson_has_review(db: AsyncSession, lesson_id: UUID) -> bool:
    result = await db.execute(select(Review.id).where(Review.lesson_id == lesson_id).limit(1))
    return result.scalar_one_or_none() is not None


async def student_has_completed_lesson_with_tutor(
    db: AsyncSession, student_id: UUID, tutor_id: UUID
) -> bool:
    result = await db.execute(
        select(
            exists(
                select(Lesson.id).where(
                    Lesson.student_id == student_id,
                    Lesson.tutor_id == tutor_id,
                    Lesson.status == LessonStatus.completed,
                )
            )
        )
    )
    return bool(result.scalar())


async def student_has_reviewed_tutor(db: AsyncSession, student_id: UUID, tutor_id: UUID) -> bool:
    result = await db.execute(
        select(Review.id).where(Review.student_id == student_id, Review.tutor_id == tutor_id).limit(1)
    )
    return result.scalar_one_or_none() is not None


async def book_lesson(db: AsyncSession, student: User, slot_id: UUID, subject: str) -> Lesson:
    if student.role != UserRole.student:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуется доступ ученика")

    result = await db.execute(
        select(AvailabilitySlot).where(AvailabilitySlot.id == slot_id).with_for_update()
    )
    slot = result.scalar_one_or_none()
    if slot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Слот не найден")

    if slot.starts_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя забронировать прошедший слот")

    if slot.tutor_id == student.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя забронировать свой собственный слот")

    profile_result = await db.execute(
        select(TutorProfile).where(TutorProfile.user_id == slot.tutor_id)
    )
    profile = profile_result.scalar_one_or_none()
    if profile is None or not subject_allowed_for_tutor(subject, profile.subjects):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Выберите предмет из списка предметов репетитора",
        )

    lesson_type = await resolve_lesson_type(db, student.id, slot.tutor_id)

    existing_result = await db.execute(select(Lesson).where(Lesson.slot_id == slot_id))
    existing_lesson = existing_result.scalar_one_or_none()

    if existing_lesson is not None:
        if existing_lesson.status == LessonStatus.scheduled:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Слот уже забронирован")
        if existing_lesson.status == LessonStatus.completed:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Слот уже использован")
        if existing_lesson.status == LessonStatus.cancelled:
            existing_lesson.student_id = student.id
            existing_lesson.status = LessonStatus.scheduled
            existing_lesson.subject = subject
            existing_lesson.lesson_type = lesson_type
            existing_lesson.meeting_url = profile.default_meeting_url if profile else None
            existing_lesson.recording_url = None
            existing_lesson.cancellation_reason = None
            slot.is_booked = True
            await db.flush()
            lesson_type_label = "пробное" if lesson_type == LessonType.trial else "повторное"
            await create_notification(
                db,
                user_id=slot.tutor_id,
                type=NotificationType.lesson_booked,
                title="Новая запись на занятие",
                message=f"Ученик {student.full_name} записался на {lesson_type_label} занятие по предмету «{subject}».",
                related_lesson_id=existing_lesson.id,
            )
            await db.commit()
            return existing_lesson

    if slot.is_booked:
        active_result = await db.execute(
            select(Lesson).where(
                Lesson.slot_id == slot_id,
                Lesson.status == LessonStatus.scheduled,
            )
        )
        if active_result.scalar_one_or_none() is None:
            slot.is_booked = False
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Слот уже забронирован")

    slot.is_booked = True
    lesson = Lesson(
        student_id=student.id,
        tutor_id=slot.tutor_id,
        slot_id=slot.id,
        status=LessonStatus.scheduled,
        subject=subject,
        lesson_type=lesson_type,
        meeting_url=profile.default_meeting_url if profile else None,
    )
    db.add(lesson)
    await db.flush()

    tutor_result = await db.execute(select(User).where(User.id == slot.tutor_id))
    tutor = tutor_result.scalar_one_or_none()
    if tutor:
        lesson_type_label = "пробное" if lesson_type == LessonType.trial else "повторное"
        await create_notification(
            db,
            user_id=slot.tutor_id,
            type=NotificationType.lesson_booked,
            title="Новая запись на занятие",
            message=f"Ученик {student.full_name} записался на {lesson_type_label} занятие по предмету «{subject}».",
            related_lesson_id=lesson.id,
        )

    await db.commit()
    return lesson
