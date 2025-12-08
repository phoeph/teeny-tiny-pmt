"""
认证API路由
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import auth_service
from app.schemas.auth import UserLogin, Token, CurrentUserResponse
from app.dependencies.auth import get_current_user, create_current_user_response
from app.config import settings
from app.models import User


router = APIRouter(prefix="/api/auth", tags=["认证"])
security = HTTPBearer()


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    
    支持用户名或邮箱前缀登录
    """
    # 认证用户
    user = await auth_service.authenticate_user(
        db, login_data.login_field, login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名/邮箱前缀或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60  # 转换为秒
    )


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息
    """
    return create_current_user_response(current_user)


@router.post("/logout")
async def logout():
    """
    用户登出
    
    注意：由于JWT是无状态的，这里只是提供一个接口，
    实际应用中需要在客户端删除令牌
    """
    return {"message": "登出成功"}


@router.get("/demo-users")
async def get_demo_users(db: AsyncSession = Depends(get_db)):
    """
    获取演示用户列表（用于前端演示登录）
    
    返回预设的演示用户信息
    """
    # 查询演示用户
    from sqlalchemy import select
    stmt = select(User).where(User.username.in_([
        "张三", "李四", "王五", "赵六", "钱七"
    ]))
    result = await db.execute(stmt)
    demo_users = result.scalars().all()
    
    if not demo_users:
        # 如果没有演示用户，返回空列表
        return {"users": []}
    
    # 创建响应数据
    users_data = []
    for user in demo_users:
        user_response = create_current_user_response(user)
        users_data.append({
            "username": user.username,
            "email_prefix": user.email_prefix,
            "display_name": user.username  # 使用用户名作为显示名
        })
    
    return {"users": users_data}