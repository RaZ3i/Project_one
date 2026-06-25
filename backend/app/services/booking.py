from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lesson import Lesson, LessonStatus
from app.models.slot import AvailabilitySlot
from app.models.tutor_profile import TutorProfile
from app.models.user import User, UserRole
from app.schemas.lesson import LessonResponse


def get_effective_meeting_url(lesson: Lesson) -> str | None:
    if lesson.meeting_url:
        return lesson.meeting_url
    if lesson.tutor and lesson.tutor.tutor_profile:
        return lesson.tutor.tutor_profile.default_meeting_url
    return None


def lesson_to_response(lesson: Lesson) -> LessonResponse:
    slot = lesson.slot
    return LessonResponse(
        id=lesson.id,
        student_id=lesson.student_id,
        tutor_id=lesson.tutor_id,
        slot_id=lesson.slot_id,
        status=lesson.status,
        meeting_url=lesson.meeting_url,
        effective_meeting_url=get_effective_meeting_url(lesson),
        notes=lesson.notes,
        created_at=lesson.created_at,
        slot_starts_at=slot.starts_at if slot else None,
        slot_ends_at=slot.ends_at if slot else None,
        student_name=lesson.student.full_name if lesson.student else None,
        tutor_name=lesson.tutor.full_name if lesson.tutor else None,
    )


async def book_lesson(db: AsyncSession, student: User, slot_id: UUID) -> Lesson:
    if student.role != UserRole.student:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуется доступ ученика")

    result = await db.execute(
        select(AvailabilitySlot).where(AvailabilitySlot.id == slot_id).with_for_update()
    )
    slot = result.scalar_one_or_none()
    if slot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Слот не найден")
    if slot.is_booked:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Слот уже забронирован")

    if slot.starts_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя забронировать прошедший слот")

    if slot.tutor_id == student.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя забронировать свой собственный слот")

    profile_result = await db.execute(
        select(TutorProfile).where(TutorProfile.user_id == slot.tutor_id)
    )
    profile = profile_result.scalar_one_or_none()

    slot.is_booked = True
    lesson = Lesson(
        student_id=student.id,
        tutor_id=slot.tutor_id,
        slot_id=slot.id,
        status=LessonStatus.scheduled,
        meeting_url=profile.default_meeting_url if profile else None,
    )
    db.add(lesson)
    await db.flush()
    await db.commit()
    return lesson
