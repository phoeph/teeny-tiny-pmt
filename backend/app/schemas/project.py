"""
项目相关的Pydantic模型
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """项目基础模型"""
    name: str = Field(..., min_length=1, max_length=200, description="项目名称")
    description: Optional[str] = Field(None, max_length=1000, description="项目描述")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")


class ProjectCreate(ProjectBase):
    """创建项目请求模型"""
    pass


class ProjectUpdate(BaseModel):
    """更新项目请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="项目名称")
    description: Optional[str] = Field(None, max_length=1000, description="项目描述")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    status: Optional[str] = Field(None, pattern="^(active|archived)$", description="项目状态")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$", description="项目优先级")
    creator_id: Optional[int] = Field(None, description="创建人ID（Reporter）")
    creator_prefix: Optional[str] = Field(None, min_length=1, max_length=100, description="创建人邮箱前缀")
    creator_email: Optional[str] = Field(None, min_length=3, max_length=200, description="创建人邮箱")
    owner_id: Optional[int] = Field(None, description="所有者ID（Assignee/Owner）")
    owner_prefix: Optional[str] = Field(None, min_length=1, max_length=100, description="所有者邮箱前缀")
    owner_email: Optional[str] = Field(None, min_length=3, max_length=200, description="所有者邮箱")
    label_path: Optional[str] = Field(None, max_length=500, description="标签完整路径（仅叶子）")


class ProjectResponse(ProjectBase):
    """项目响应模型"""
    id: int = Field(..., description="项目ID")
    code: str = Field(..., description="项目编号")
    creator_id: int = Field(..., description="创建人ID")
    owner_id: int = Field(..., description="所有者ID")
    status: str = Field(..., description="项目状态")
    priority: str | None = Field(None, description="项目优先级")
    archived: bool = Field(..., description="是否已归档")
    created_at: datetime = Field(..., description="创建时间")
    deleted_at: Optional[datetime] = Field(None, description="删除时间")
    owner_username: Optional[str] = Field(None, description="所有者用户名")
    owner_prefix: Optional[str] = Field(None, description="所有者邮箱前缀")
    creator_username: Optional[str] = Field(None, description="创建者用户名")
    creator_prefix: Optional[str] = Field(None, description="创建者邮箱前缀")
    label_path: Optional[str] = Field(None, description="标签完整路径")
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """项目列表响应模型"""
    items: List[ProjectResponse] = Field(..., description="项目列表")
    total: int = Field(..., description="总数量")
    page: int = Field(1, description="当前页码")
    size: int = Field(10, description="每页数量")


class ProjectQuery(BaseModel):
    """项目查询参数模型"""
    status: Optional[str] = Field(None, description="项目状态筛选")
    archived: Optional[bool] = Field(None, description="归档状态筛选")
    include_deleted: Optional[bool] = Field(False, description="是否包含已删除的项目")
    search: Optional[str] = Field(None, description="搜索关键词（名称或描述）")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
