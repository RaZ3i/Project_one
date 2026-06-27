from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_tutor
from app.core.database import get_db
from app.models.review import Review
from app.models.tutor_profile import TutorProfile
from app.models.user import User, UserRole
from app.schemas.review import ReviewResponse
from app.schemas.tutor import TutorDetail, TutorListItem, TutorProfileUpdate

router = APIRouter(prefix="/tutors", tags=["tutors"])


async def _review_stats(db: AsyncSession, tutor_id: UUID) -> tuple[float | None, int]:
    result = await db.execute(
        select(func.avg(Review.rating), func.count(Review.id)).where(Review.tutor_id == tutor_id)
    )
    row = result.one()
    avg_rating = round(float(row[0]), 1) if row[0] is not None else None
    review_count = int(row[1] or 0)
    return avg_rating, review_count


@router.get("", response_model=list[TutorListItem])
async def list_tutors(
    db: Annotated[AsyncSession, Depends(get_db)],
    subject: str | None = Query(default=None),
):
    query = (
        select(User)
        .where(User.role == UserRole.tutor)
        .options(selectinload(User.tutor_profile))
    )
    if subject:
        query = query.join(TutorProfile, TutorProfile.user_id == User.id).where(
            TutorProfile.subjects.ilike(f"%{subject}%")
        )

    result = await db.execute(query)
    tutors = result.scalars().unique().all()
    items = []
    for tutor in tutors:
        profile = tutor.tutor_profile
        avg_rating, review_count = await _review_stats(db, tutor.id)
        items.append(
            TutorListItem(
                id=tutor.id,
                full_name=tutor.full_name,
                subjects=profile.subjects if profile else None,
                bio=profile.bio if profile else None,
                avatar_url=tutor.avatar_url,
                avg_rating=avg_rating,
                review_count=review_count,
            )
        )
    return items


@router.get("/{tutor_id}/reviews", response_model=list[ReviewResponse])
async def list_tutor_reviews(tutor_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(Review, User.full_name)
        .join(User, User.id == Review.student_id)
        .where(Review.tutor_id == tutor_id)
        .order_by(Review.created_at.desc())
    )
    rows = result.all()
    return [
        ReviewResponse(
            id=review.id,
            student_id=review.student_id,
            tutor_id=review.tutor_id,
            lesson_id=review.lesson_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
            student_name=student_name,
        )
        for review, student_name in rows
    ]


@router.get("/{tutor_id}", response_model=TutorDetail)
async def get_tutor(tutor_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(User)
        .where(User.id == tutor_id, User.role == UserRole.tutor)
        .options(selectinload(User.tutor_profile))
    )
    tutor = result.scalar_one_or_none()
    if tutor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Репетитор не найден")
    profile = tutor.tutor_profile
    avg_rating, review_count = await _review_stats(db, tutor.id)
    return TutorDetail(
        id=tutor.id,
        full_name=tutor.full_name,
        email=tutor.email,
        subjects=profile.subjects if profile else None,
        bio=profile.bio if profile else None,
        default_meeting_url=profile.default_meeting_url if profile else None,
        avatar_url=tutor.avatar_url,
        avg_rating=avg_rating,
        review_count=review_count,
    )


@router.put("/me/profile", response_model=TutorDetail)
async def update_my_profile(
    data: TutorProfileUpdate,
    tutor: Annotated[User, Depends(get_current_tutor)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(TutorProfile).where(TutorProfile.user_id == tutor.id))
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = TutorProfile(user_id=tutor.id)
        db.add(profile)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    await db.commit()
    await db.refresh(profile)
    await db.refresh(tutor)
    avg_rating, review_count = await _review_stats(db, tutor.id)

    return TutorDetail(
        id=tutor.id,
        full_name=tutor.full_name,
        email=tutor.email,
        subjects=profile.subjects,
        bio=profile.bio,
        default_meeting_url=profile.default_meeting_url,
        avatar_url=tutor.avatar_url,
        avg_rating=avg_rating,
        review_count=review_count,
    )
