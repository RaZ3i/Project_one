from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_student
from app.core.database import get_db
from app.models.lesson import Lesson, LessonStatus
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    data: ReviewCreate,
    student: Annotated[User, Depends(get_current_student)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    tutor_result = await db.execute(select(User).where(User.id == data.tutor_id))
    tutor = tutor_result.scalar_one_or_none()
    if tutor is None or tutor.role.value != "tutor":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Репетитор не найден")

    lesson_result = await db.execute(select(Lesson).where(Lesson.id == data.lesson_id))
    lesson = lesson_result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Занятие не найдено")
    if lesson.student_id != student.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этому занятию")
    if lesson.tutor_id != data.tutor_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Занятие не принадлежит этому репетитору")
    if lesson.status != LessonStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Отзыв можно оставить только после завершённого занятия"
        )

    existing = await db.execute(select(Review).where(Review.lesson_id == data.lesson_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Отзыв на это занятие уже оставлен")

    review = Review(
        student_id=student.id,
        tutor_id=data.tutor_id,
        lesson_id=data.lesson_id,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)

    return ReviewResponse(
        id=review.id,
        student_id=review.student_id,
        tutor_id=review.tutor_id,
        lesson_id=review.lesson_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
        student_name=student.full_name,
    )
