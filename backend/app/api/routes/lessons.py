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
from app.services.booking import book_lesson, lesson_to_response

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.post("", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    data: LessonCreate,
    student: Annotated[User, Depends(get_current_student)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        lesson = await book_lesson(db, student, data.slot_id)
    except HTTPException:
        raise
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot already booked") from e
        raise

    result = await db.execute(
        select(Lesson)
        .where(Lesson.id == lesson.id)
        .options(
            selectinload(Lesson.slot),
            selectinload(Lesson.student),
            selectinload(Lesson.tutor).selectinload(User.tutor_profile),
        )
    )
    lesson = result.scalar_one()
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

    query = query.options(
        selectinload(Lesson.slot),
        selectinload(Lesson.student),
        selectinload(Lesson.tutor).selectinload(User.tutor_profile),
    ).order_by(Lesson.created_at.desc())

    result = await db.execute(query)
    lessons = result.scalars().all()
    return [lesson_to_response(lesson) for lesson in lessons]


@router.patch("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: UUID,
    data: LessonUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Lesson)
        .where(Lesson.id == lesson_id)
        .options(
            selectinload(Lesson.slot),
            selectinload(Lesson.student),
            selectinload(Lesson.tutor).selectinload(User.tutor_profile),
        )
    )
    lesson = result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    is_student = user.role == UserRole.student and lesson.student_id == user.id
    is_tutor = user.role == UserRole.tutor and lesson.tutor_id == user.id
    if not is_student and not is_tutor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    update_data = data.model_dump(exclude_unset=True)

    if "meeting_url" in update_data and user.role != UserRole.tutor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only tutors can update meeting URL")

    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == LessonStatus.cancelled:
            pass
        elif new_status == LessonStatus.completed and user.role != UserRole.tutor:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only tutors can mark completed")

    for key, value in update_data.items():
        setattr(lesson, key, value)

    if lesson.status == LessonStatus.cancelled and lesson.slot:
        lesson.slot.is_booked = False

    await db.commit()
    await db.refresh(lesson)
    return lesson_to_response(lesson)
