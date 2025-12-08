from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class WorkItemCreate(BaseModel):
    kind: str = Field(..., pattern="^(JOB|TASK)$")
    project_id: int
    parent_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=500)
    status: str = Field("todo", pattern="^(todo|doing|blocked|done|cancelled|deleted)$")
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=2000)
    estimated_hours: Optional[float] = None


class WorkItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    status: Optional[str] = Field(None, pattern="^(todo|doing|blocked|done|cancelled|deleted)$")
    assignee_id: Optional[int] = None
    assignee_prefix: Optional[str] = Field(None, min_length=1, max_length=100)
    assignee_email: Optional[str] = Field(None, min_length=3, max_length=200)
    creator_id: Optional[int] = None
    creator_prefix: Optional[str] = Field(None, min_length=1, max_length=100)
    creator_email: Optional[str] = Field(None, min_length=3, max_length=200)
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    actual_hours: Optional[float] = None
    estimated_hours: Optional[float] = None
    label_path: Optional[str] = Field(None, max_length=500)


class WorkItemResponse(BaseModel):
    id: int
    code: str
    kind: str
    project_id: int
    parent_id: Optional[int]
    title: str
    status: str
    assignee_id: Optional[int]
    planned_start_date: Optional[date]
    planned_end_date: Optional[date]
    completed_at: Optional[datetime]
    actual_hours: Optional[float]
    estimated_hours: Optional[float]
    label_path: Optional[str]
    created_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True


class WorkItemBatchUpdateItem(BaseModel):
    id: int
    # 允许更新的一组字段，与 WorkItemUpdate 对齐（可选）
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    status: Optional[str] = Field(None, pattern="^(todo|doing|blocked|done|cancelled|deleted)$")
    assignee_id: Optional[int] = None
    assignee_prefix: Optional[str] = Field(None, min_length=1, max_length=100)
    assignee_email: Optional[str] = Field(None, min_length=3, max_length=200)
    creator_id: Optional[int] = None
    creator_prefix: Optional[str] = Field(None, min_length=1, max_length=100)
    creator_email: Optional[str] = Field(None, min_length=3, max_length=200)
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    actual_hours: Optional[float] = None
    estimated_hours: Optional[float] = None


class WorkItemBatchUpdateRequest(BaseModel):
    items: list[WorkItemBatchUpdateItem]
