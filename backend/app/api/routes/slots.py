from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_tutor
from app.core.database import get_db
from app.models.lesson import Lesson, LessonStatus
from app.models.slot import AvailabilitySlot
from app.models.user import User
from app.schemas.slot import SlotCreate, SlotResponse
from app.services.booking import slot_is_actively_booked

router = APIRouter(prefix="/slots", tags=["slots"])


@router.get("", response_model=list[SlotResponse])
async def list_slots(
    db: Annotated[AsyncSession, Depends(get_db)],
    tutor_id: UUID = Query(...),
    available_only: bool = Query(True),
):
    query = (
        select(AvailabilitySlot)
        .outerjoin(Lesson, AvailabilitySlot.id == Lesson.slot_id)
        .where(AvailabilitySlot.tutor_id == tutor_id)
        .options(selectinload(AvailabilitySlot.lesson))
    )
    if available_only:
        query = query.where(
            AvailabilitySlot.starts_at > datetime.now(timezone.utc),
            or_(
                Lesson.id.is_(None),
                Lesson.status != LessonStatus.scheduled,
            ),
        )
    query = query.order_by(AvailabilitySlot.starts_at)
    result = await db.execute(query)
    slots = result.scalars().unique().all()
    for slot in slots:
        slot.is_booked = slot_is_actively_booked(slot)
    return slots


@router.post("", response_model=SlotResponse, status_code=status.HTTP_201_CREATED)
async def create_slot(
    data: SlotCreate,
    tutor: Annotated[User, Depends(get_current_tutor)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if data.starts_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Слот должен быть в будущем")

    slot = AvailabilitySlot(
        tutor_id=tutor.id,
        starts_at=data.starts_at,
        ends_at=data.ends_at,
    )
    db.add(slot)
    await db.commit()
    await db.refresh(slot)
    return slot


@router.delete("/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_slot(
    slot_id: UUID,
    tutor: Annotated[User, Depends(get_current_tutor)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(AvailabilitySlot)
        .where(
            AvailabilitySlot.id == slot_id,
            AvailabilitySlot.tutor_id == tutor.id,
        )
        .options(selectinload(AvailabilitySlot.lesson))
    )
    slot = result.scalar_one_or_none()
    if slot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Слот не найден")
    if slot_is_actively_booked(slot):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя удалить забронированный слот")

    await db.delete(slot)
    await db.commit()
