from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.tutor_profile import TutorProfile
from app.models.user import User, UserRole
from app.schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: Annotated[AsyncSession, Depends(get_db)]):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=data.email,
        password_hash=get_password_hash(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    await db.flush()

    if data.role == UserRole.tutor:
        db.add(TutorProfile(user_id=user.id, bio="", subjects=""))

    await db.commit()
    await db.refresh(user)

    token = create_access_token(str(user.id), {"role": user.role.value})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(str(user.id), {"role": user.role.value})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def me(user: Annotated[User, Depends(get_current_user)]):
    return UserResponse.model_validate(user)
