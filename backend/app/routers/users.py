from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.database import get_db
from app.models import User
from app.dependencies.auth import get_current_user
from app.schemas.user import UpdateMeRequest, UserProfileResponse
from sqlalchemy.exc import IntegrityError
from app.services.auth_service import auth_service
from pydantic import BaseModel, Field
from typing import List

router = APIRouter(prefix="/api/users", tags=["users"])

ALLOWED_AVATARS = {"cat_1","cat_2","cat_3","dog_1","dog_2","dog_3"}


@router.patch("/me", response_model=UserProfileResponse)
async def update_me(payload: UpdateMeRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.avatar_key is not None and payload.avatar_key not in ALLOWED_AVATARS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"code":"INVALID_AVATAR","message":"头像不合法"})

    stmt = select(User).where(User.id == current_user.id)
    res = await db.execute(stmt)
    user: User | None = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code":"USER_NOT_FOUND","message":"用户不存在"})

    if payload.username is not None or payload.email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"code":"IMMUTABLE_FIELD","message":"用户名和邮箱不可修改"})
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.avatar_key is not None:
        user.avatar_key = payload.avatar_key

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code":"UNIQUE_CONSTRAINT","message":"唯一性冲突"})
    await db.refresh(user)
    return UserProfileResponse.model_validate(user)


@router.get("/", response_model=list[dict])
async def list_users(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(User).where(User.is_active == True)
    res = await db.execute(stmt)
    users = res.scalars().all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email_prefix": u.email_prefix,
            "full_name": getattr(u, "full_name", None),
            "email": getattr(u, "email", None),
        }
        for u in users
    ]


class UserSeed(BaseModel):
    email: str = Field(..., description="邮箱")
    full_name: str = Field(..., description="姓名")


@router.post("/reset")
async def reset_users(payload: List[UserSeed], db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user or (current_user.username != 'admin'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code":"FORBIDDEN","message":"需要管理员权限"})

    stmt_deactivate = update(User).where(User.username != 'admin').values(is_active=False)
    await db.execute(stmt_deactivate)

    admin_stmt = select(User).where(User.username == 'admin')
    admin_res = await db.execute(admin_stmt)
    admin_user = admin_res.scalar_one_or_none()
    if admin_user:
        admin_user.is_active = True
        await db.flush()

    for seed in payload:
        prefix = (seed.email.split('@')[0]).strip()
        username = prefix
        email = seed.email.strip()
        full_name = seed.full_name.strip()

        stmt = select(User).where((User.email_prefix == prefix) | (User.username == username))
        res = await db.execute(stmt)
        user: User | None = res.scalar_one_or_none()
        if user:
            user.username = username
            user.email_prefix = prefix
            user.email = email
            user.full_name = full_name
            user.is_active = True
        else:
            hashed = auth_service.get_password_hash("123456")
            user = User(
                username=username,
                email_prefix=prefix,
                email=email,
                full_name=full_name,
                password_hash=hashed,
                is_active=True,
            )
            db.add(user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code":"UNIQUE_CONSTRAINT","message":"唯一性冲突"})
    return {"ok": True}
