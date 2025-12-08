"""
认证相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class UserLogin(BaseModel):
    """用户登录模型"""
    login_field: str = Field(..., description="用户名或邮箱前缀")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """令牌响应模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email_prefix: str = Field(..., description="邮箱前缀")
    email: Optional[str] = Field(default=None, description="邮箱")
    full_name: Optional[str] = Field(default=None, description="姓名")
    is_active: bool = Field(..., description="是否激活")
    phone: Optional[str] = Field(default=None, description="手机号")
    avatar_key: Optional[str] = Field(default=None, description="头像键")
    created_at: str = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class CurrentUserResponse(BaseModel):
    """当前用户响应模型"""
    user: UserResponse = Field(..., description="用户信息")
    permissions: list[str] = Field(default_factory=list, description="用户权限")
