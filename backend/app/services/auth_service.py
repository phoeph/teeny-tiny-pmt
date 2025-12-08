"""
认证服务 - 支持中文名与邮箱前缀登录
"""
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from app.config import settings


class AuthService:
    """认证服务"""
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def get_password_hash(self, password: str) -> str:
        """获取密码哈希"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            username: str = payload.get("sub")
            if username is None:
                return None
            return {"username": username}
        except JWTError:
            return None
    
    async def authenticate_user(self, session: AsyncSession, login_field: str, password: str) -> Optional[User]:
        """
        认证用户 - 支持用户名或邮箱前缀登录
        
        Args:
            session: 数据库会话
            login_field: 用户名或邮箱前缀
            password: 密码
            
        Returns:
            用户对象，如果认证失败返回None
        """
        # 查询用户（支持用户名或邮箱前缀登录）
        stmt = select(User).where(
            (User.username == login_field) | (User.email_prefix == login_field)
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # 验证密码
        if not self.verify_password(password, user.password_hash):
            return None
        
        # 检查用户是否激活
        if not user.is_active:
            return None
        
        return user
    
    async def get_current_user(self, session: AsyncSession, token: str) -> Optional[User]:
        """
        获取当前用户
        
        Args:
            session: 数据库会话
            token: JWT令牌
            
        Returns:
            用户对象，如果令牌无效返回None
        """
        token_data = self.verify_token(token)
        if not token_data:
            return None
        
        username = token_data.get("username")
        if not username:
            return None
        
        # 查询用户
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return None
        
        return user


# 创建全局实例
auth_service = AuthService()