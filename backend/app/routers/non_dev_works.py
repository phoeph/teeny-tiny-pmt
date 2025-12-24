from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select
from datetime import date

from app.database import get_db
from app.models import ProjectNonDevWork, Project, User
from app.dependencies.auth import get_current_user
from app.exceptions import AppException
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/non-dev-works", tags=["non-dev-works"])


class NonDevWorkCreate(BaseModel):
    project_id: int
    report_period_start: date
    report_period_end: date
    work_type: str = "other_work"  # other_work, next_week_plan
    title: str
    description: Optional[str] = None


class NonDevWorkUpdate(BaseModel):
    work_type: Optional[str] = None  # other_work, next_week_plan
    title: Optional[str] = None
    description: Optional[str] = None


class NonDevWorkResponse(BaseModel):
    id: int
    project_id: int
    report_period_start: date
    report_period_end: date
    work_type: str
    title: str
    description: Optional[str]
    creator_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/", response_model=NonDevWorkResponse)
async def create_non_dev_work(
    work_data: NonDevWorkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建非开发工作说明"""
    
    # 验证项目是否存在
    project_stmt = select(Project).where(
        and_(Project.id == work_data.project_id, Project.deleted_at.is_(None))
    )
    project_result = await db.execute(project_stmt)
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROJECT_NOT_FOUND", "message": "项目不存在"}
        )
    
    # 创建非开发工作记录
    non_dev_work = ProjectNonDevWork(
        project_id=work_data.project_id,
        report_period_start=work_data.report_period_start,
        report_period_end=work_data.report_period_end,
        work_type=work_data.work_type,
        title=work_data.title,
        description=work_data.description,
        creator_id=current_user.id
    )
    
    db.add(non_dev_work)
    await db.commit()
    await db.refresh(non_dev_work)
    
    return non_dev_work


@router.get("/by-report", response_model=List[NonDevWorkResponse])
async def get_non_dev_works_by_report(
    project_ids: str = Query(..., description="项目ID列表，逗号分隔"),
    start_date: date = Query(..., description="报告开始日期"),
    end_date: date = Query(..., description="报告结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """根据周报期间获取非开发工作说明列表"""
    
    # 解析项目ID列表
    try:
        project_id_list = [int(pid.strip()) for pid in project_ids.split(',') if pid.strip()]
    except ValueError:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_PROJECT_IDS", "message": "项目ID格式错误"}
        )
    
    if not project_id_list:
        return []
    
    # 查询指定项目和时间范围内的非开发工作
    stmt = select(ProjectNonDevWork).where(
        and_(
            ProjectNonDevWork.project_id.in_(project_id_list),
            ProjectNonDevWork.deleted_at.is_(None),
            # 时间范围重叠检查：报告期间与工作记录期间有重叠
            ProjectNonDevWork.report_period_start <= end_date,
            ProjectNonDevWork.report_period_end >= start_date
        )
    ).order_by(
        ProjectNonDevWork.project_id,
        ProjectNonDevWork.report_period_start,
        ProjectNonDevWork.created_at.desc()
    )
    
    result = await db.execute(stmt)
    non_dev_works = result.scalars().all()
    
    return non_dev_works


@router.get("/project/{project_id}", response_model=List[NonDevWorkResponse])
async def get_project_non_dev_works(
    project_id: int,
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目的非开发工作说明列表"""
    
    # 验证项目是否存在
    project_stmt = select(Project).where(
        and_(Project.id == project_id, Project.deleted_at.is_(None))
    )
    project_result = await db.execute(project_stmt)
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROJECT_NOT_FOUND", "message": "项目不存在"}
        )
    
    # 构建查询条件
    stmt = select(ProjectNonDevWork).where(
        and_(
            ProjectNonDevWork.project_id == project_id,
            ProjectNonDevWork.deleted_at.is_(None)
        )
    )
    
    # 如果提供了日期范围，添加时间过滤
    if start_date and end_date:
        stmt = stmt.where(
            and_(
                ProjectNonDevWork.report_period_start <= end_date,
                ProjectNonDevWork.report_period_end >= start_date
            )
        )
    
    stmt = stmt.order_by(
        ProjectNonDevWork.report_period_start.desc(),
        ProjectNonDevWork.created_at.desc()
    )
    
    result = await db.execute(stmt)
    non_dev_works = result.scalars().all()
    
    return non_dev_works


@router.put("/{work_id}", response_model=NonDevWorkResponse)
async def update_non_dev_work(
    work_id: int,
    work_data: NonDevWorkUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新非开发工作说明"""
    
    # 查找记录
    stmt = select(ProjectNonDevWork).where(
        and_(
            ProjectNonDevWork.id == work_id,
            ProjectNonDevWork.deleted_at.is_(None)
        )
    )
    result = await db.execute(stmt)
    non_dev_work = result.scalar_one_or_none()
    
    if not non_dev_work:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NON_DEV_WORK_NOT_FOUND", "message": "非开发工作记录不存在"}
        )
    
    # 更新字段
    if work_data.work_type is not None:
        non_dev_work.work_type = work_data.work_type
    if work_data.title is not None:
        non_dev_work.title = work_data.title
    if work_data.description is not None:
        non_dev_work.description = work_data.description
    
    non_dev_work.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(non_dev_work)
    
    return non_dev_work


@router.delete("/{work_id}")
async def delete_non_dev_work(
    work_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除非开发工作说明"""
    
    # 查找记录
    stmt = select(ProjectNonDevWork).where(
        and_(
            ProjectNonDevWork.id == work_id,
            ProjectNonDevWork.deleted_at.is_(None)
        )
    )
    result = await db.execute(stmt)
    non_dev_work = result.scalar_one_or_none()
    
    if not non_dev_work:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NON_DEV_WORK_NOT_FOUND", "message": "非开发工作记录不存在"}
        )
    
    # 软删除
    non_dev_work.deleted_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "删除成功"}