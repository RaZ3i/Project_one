from fastapi import APIRouter

from app.core.subjects import SUBJECTS

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("")
async def list_subjects():
    return SUBJECTS
