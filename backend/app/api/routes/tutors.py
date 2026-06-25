from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_tutor
from app.core.database import get_db
from app.models.tutor_profile import TutorProfile
from app.models.user import User, UserRole
from app.schemas.tutor import TutorDetail, TutorListItem, TutorProfileUpdate

router = APIRouter(prefix="/tutors", tags=["tutors"])


@router.get("", response_model=list[TutorListItem])
async def list_tutors(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(User)
        .where(User.role == UserRole.tutor)
        .options(selectinload(User.tutor_profile))
    )
    tutors = result.scalars().all()
    items = []
    for tutor in tutors:
        profile = tutor.tutor_profile
        items.append(
            TutorListItem(
                id=tutor.id,
                full_name=tutor.full_name,
                subjects=profile.subjects if profile else None,
                bio=profile.bio if profile else None,
            )
        )
    return items


@router.get("/{tutor_id}", response_model=TutorDetail)
async def get_tutor(tutor_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(User)
        .where(User.id == tutor_id, User.role == UserRole.tutor)
        .options(selectinload(User.tutor_profile))
    )
    tutor = result.scalar_one_or_none()
    if tutor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tutor not found")
    profile = tutor.tutor_profile
    return TutorDetail(
        id=tutor.id,
        full_name=tutor.full_name,
        email=tutor.email,
        subjects=profile.subjects if profile else None,
        bio=profile.bio if profile else None,
        default_meeting_url=profile.default_meeting_url if profile else None,
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

    return TutorDetail(
        id=tutor.id,
        full_name=tutor.full_name,
        email=tutor.email,
        subjects=profile.subjects,
        bio=profile.bio,
        default_meeting_url=profile.default_meeting_url,
    )
