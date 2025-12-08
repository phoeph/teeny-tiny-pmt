"""
认证依赖项
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.services.auth_service import auth_service
from app.schemas.auth import CurrentUserResponse, UserResponse


# 使用HTTP Bearer认证
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前用户
    
    Args:
        credentials: HTTP认证凭据
        db: 数据库会话
        
    Returns:
        当前用户对象
        
    Raises:
        HTTPException: 如果认证失败
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    token = credentials.credentials
    user = await auth_service.get_current_user(db, token)
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    可选的当前用户（用于公开接口）
    
    Args:
        credentials: HTTP认证凭据（可选）
        db: 数据库会话
        
    Returns:
        当前用户对象，如果没有认证则为None
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        return await auth_service.get_current_user(db, token)
    except Exception:
        return None


def create_user_response(user: User) -> UserResponse:
    """创建用户响应模型"""
    return UserResponse(
        id=user.id,
        username=user.username,
        email_prefix=user.email_prefix,
        email=getattr(user, "email", None),
        full_name=getattr(user, "full_name", None),
        is_active=user.is_active,
        phone=getattr(user, "phone", None),
        avatar_key=getattr(user, "avatar_key", None),
        created_at=user.created_at.isoformat() if user.created_at else None
    )


def create_current_user_response(user: User) -> CurrentUserResponse:
    """创建当前用户响应模型"""
    user_response = create_user_response(user)
    # TODO: 根据用户角色和权限设置实际的权限列表
    permissions = []
    
    return CurrentUserResponse(
        user=user_response,
        permissions=permissions
    )
