from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import AvatarUploadResponse, UserProfileResponse, UserProfileUpdate

router = APIRouter(prefix="/users", tags=["users"])

AVATAR_DIR = Path(__file__).resolve().parent.parent.parent.parent / "static" / "uploads" / "avatars"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_my_profile(user: Annotated[User, Depends(get_current_user)]):
    return UserProfileResponse.model_validate(user)


@router.put("/me/profile", response_model=UserProfileResponse)
async def update_my_profile(
    data: UserProfileUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return UserProfileResponse.model_validate(user)


@router.post("/me/avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Допустимые форматы: JPEG, PNG, WebP",
        )

    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    dest = AVATAR_DIR / f"{user.id}.jpg"
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Файл слишком большой (макс. 5 МБ)")

    dest.write_bytes(content)
    avatar_url = f"/uploads/avatars/{user.id}.jpg"
    user.avatar_url = avatar_url
    await db.commit()
    return AvatarUploadResponse(avatar_url=avatar_url)
