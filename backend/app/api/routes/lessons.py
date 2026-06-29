from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_student, get_current_user
from app.core.database import get_db
from app.models.lesson import Lesson, LessonStatus
from app.models.user import User, UserRole
from app.schemas.lesson import LessonCreate, LessonResponse, LessonUpdate
from app.services.booking import (
    book_lesson,
    cancel_lesson_booking,
    lesson_has_review,
    lesson_to_response,
)

router = APIRouter(prefix="/lessons", tags=["lessons"])

_LESSON_LOAD = (
    selectinload(Lesson.slot),
    selectinload(Lesson.student),
    selectinload(Lesson.tutor).selectinload(User.tutor_profile),
)


async def _load_lesson(db: AsyncSession, lesson_id: UUID) -> Lesson | None:
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id).options(*_LESSON_LOAD)
    )
    return result.scalar_one_or_none()


def _user_can_access_lesson(user: User, lesson: Lesson) -> bool:
    if user.role == UserRole.student and lesson.student_id == user.id:
        return True
    if user.role == UserRole.tutor and lesson.tutor_id == user.id:
        return True
    return False


@router.post("", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    data: LessonCreate,
    student: Annotated[User, Depends(get_current_student)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        lesson = await book_lesson(db, student, data.slot_id, data.subject)
    except HTTPException:
        raise
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Слот уже забронирован") from e
        raise

    lesson = await _load_lesson(db, lesson.id)
    assert lesson is not None
    return lesson_to_response(lesson)


@router.get("/me", response_model=list[LessonResponse])
async def my_lessons(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if user.role == UserRole.student:
        query = select(Lesson).where(Lesson.student_id == user.id)
    else:
        query = select(Lesson).where(Lesson.tutor_id == user.id)

    query = query.options(*_LESSON_LOAD).order_by(Lesson.created_at.desc())

    result = await db.execute(query)
    lessons = result.scalars().all()
    responses = []
    for lesson in lessons:
        has_review = False
        if user.role == UserRole.student:
            has_review = await lesson_has_review(db, lesson.id)
        responses.append(lesson_to_response(lesson, has_review=has_review))
    return responses


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    lesson = await _load_lesson(db, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Занятие не найдено")
    if not _user_can_access_lesson(user, lesson):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")

    has_review = False
    if user.role == UserRole.student:
        has_review = await lesson_has_review(db, lesson.id)
    return lesson_to_response(lesson, has_review=has_review)


@router.patch("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: UUID,
    data: LessonUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    lesson = await _load_lesson(db, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Занятие не найдено")

    if not _user_can_access_lesson(user, lesson):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")

    update_data = data.model_dump(exclude_unset=True)

    if "meeting_url" in update_data and user.role != UserRole.tutor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Только репетиторы могут обновлять ссылку на встречу"
        )

    if "recording_url" in update_data:
        if user.role != UserRole.tutor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Только репетиторы могут добавлять ссылку на запись"
            )
        if lesson.status != LessonStatus.completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ссылку на запись можно добавить только после завершения занятия",
            )

    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == LessonStatus.cancelled:
            pass
        elif new_status == LessonStatus.completed and user.role != UserRole.tutor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Только репетиторы могут отмечать занятия как завершённые"
            )

    if update_data.get("status") == LessonStatus.cancelled:
        await cancel_lesson_booking(db, lesson)
        update_data.pop("status", None)

    for key, value in update_data.items():
        setattr(lesson, key, value)

    await db.commit()
    await db.refresh(lesson)
    lesson = await _load_lesson(db, lesson.id)
    assert lesson is not None

    has_review = False
    if user.role == UserRole.student:
        has_review = await lesson_has_review(db, lesson.id)
    return lesson_to_response(lesson, has_review=has_review)
