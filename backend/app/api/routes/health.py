import os

from fastapi import APIRouter

router = APIRouter(tags=["health"])

BUILD_ID = os.getenv("BUILD_ID") or os.getenv("RAILWAY_GIT_COMMIT_SHA") or "dev"


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/build-info")
async def build_info():
    return {"build_id": BUILD_ID, "status": "ok"}
