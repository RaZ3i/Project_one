from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tutor
from app.core.database import get_db
from app.models.slot import AvailabilitySlot
from app.models.user import User
from app.schemas.slot import SlotCreate, SlotResponse

router = APIRouter(prefix="/slots", tags=["slots"])


@router.get("", response_model=list[SlotResponse])
async def list_slots(
    db: Annotated[AsyncSession, Depends(get_db)],
    tutor_id: UUID = Query(...),
    available_only: bool = Query(True),
):
    query = select(AvailabilitySlot).where(AvailabilitySlot.tutor_id == tutor_id)
    if available_only:
        query = query.where(
            AvailabilitySlot.is_booked == False,  # noqa: E712
            AvailabilitySlot.starts_at > datetime.now(timezone.utc),
        )
    query = query.order_by(AvailabilitySlot.starts_at)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=SlotResponse, status_code=status.HTTP_201_CREATED)
async def create_slot(
    data: SlotCreate,
    tutor: Annotated[User, Depends(get_current_tutor)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if data.starts_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slot must be in the future")

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
        select(AvailabilitySlot).where(
            AvailabilitySlot.id == slot_id,
            AvailabilitySlot.tutor_id == tutor.id,
        )
    )
    slot = result.scalar_one_or_none()
    if slot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found")
    if slot.is_booked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete booked slot")

    await db.delete(slot)
    await db.commit()
