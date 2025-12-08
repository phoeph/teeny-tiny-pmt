from pydantic import BaseModel, Field
from typing import Optional


class UpdateMeRequest(BaseModel):
    username: Optional[str] = Field(default=None, description="用户名")
    full_name: Optional[str] = Field(default=None, description="姓名")
    email: Optional[str] = Field(default=None, description="邮箱")
    phone: Optional[str] = Field(default=None, description="手机号")
    avatar_key: Optional[str] = Field(default=None, description="头像键")


class UserProfileResponse(BaseModel):
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email_prefix: str = Field(..., description="邮箱前缀")
    email: Optional[str] = Field(default=None, description="邮箱")
    full_name: Optional[str] = Field(default=None, description="姓名")
    is_active: bool = Field(..., description="是否激活")
    phone: Optional[str] = Field(default=None, description="手机号")
    avatar_key: Optional[str] = Field(default=None, description="头像键")
    created_at: Optional[str] = Field(default=None, description="创建时间")

    class Config:
        from_attributes = True
