"""
项目API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.project_service import project_service
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, 
    ProjectListResponse, ProjectQuery
)
from app.dependencies.auth import get_current_user
from app.models import User
from app.exceptions import AppException


router = APIRouter(prefix="/api/projects", tags=["项目"])


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新项目
    
    自动生成项目编号（PRO开头）
    """
    try:
        project = await project_service.create_project(
            db, project_data, current_user.id
        )
        return project
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    include_deleted: bool = Query(False, description="是否包含已删除的项目"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取项目详情
    """
    try:
        project = await project_service.get_project(
            db, project_id, include_deleted=include_deleted
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 拼接可展示的创建者/所有者前缀与用户名
        from sqlalchemy import select
        owner = None
        creator = None
        if project.owner_id:
            res_o = await db.execute(select(User).where(User.id == project.owner_id))
            owner = res_o.scalars().first()
        if project.creator_id:
            res_c = await db.execute(select(User).where(User.id == project.creator_id))
            creator = res_c.scalars().first()
        return {
            "id": project.id,
            "code": project.code,
            "name": project.name,
            "description": project.description,
            "priority": project.priority,
            "start_date": project.start_date,
            "end_date": project.end_date,
            "creator_id": project.creator_id,
            "owner_id": project.owner_id,
            "status": project.status,
            "archived": project.archived,
            "created_at": project.created_at,
            "deleted_at": project.deleted_at,
            "owner_username": owner.username if owner else None,
            "owner_prefix": owner.email_prefix if owner else None,
            "creator_username": creator.username if creator else None,
            "creator_prefix": creator.email_prefix if creator else None,
            "label_path": project.label_path,
        }
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    status: Optional[str] = Query(None, description="项目状态筛选"),
    archived: Optional[bool] = Query(None, description="归档状态筛选"),
    include_deleted: bool = Query(False, description="是否包含已删除的项目"),
    search: Optional[str] = Query(None, description="搜索关键词（名称或描述）"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取项目列表
    
    支持分页、筛选、搜索功能
    """
    try:
        # 构建查询参数
        query_params = ProjectQuery(
            status=status,
            archived=archived,
            include_deleted=include_deleted,
            search=search,
            page=page,
            size=size
        )
        
        projects, total = await project_service.list_projects(
            db, query_params, current_user.id
        )
        
        return ProjectListResponse(
            items=projects,
            total=total,
            page=page,
            size=size
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新项目
    
    只有项目所有者可以更新项目
    已归档的项目不能修改
    """
    try:
        project = await project_service.update_project(
            db, project_id, project_data, current_user.id
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        return project
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    归档项目
    
    只有项目所有者可以归档项目
    """
    try:
        project = await project_service.archive_project(
            db, project_id, current_user.id
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        return project
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/{project_id}/unarchive", response_model=ProjectResponse)
async def unarchive_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消归档项目
    
    只有项目所有者可以取消归档项目
    """
    try:
        project = await project_service.unarchive_project(
            db, project_id, current_user.id
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        return project
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete("/{project_id}", response_model=ProjectResponse)
async def soft_delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    软删除项目
    
    只有项目所有者可以删除项目
    项目会被标记为已删除，但不会从数据库中物理删除
    """
    try:
        project = await project_service.soft_delete_project(
            db, project_id, current_user.id
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        return project
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/{project_id}/restore", response_model=ProjectResponse)
async def restore_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    恢复软删除的项目
    
    只有项目所有者可以恢复项目
    """
    try:
        project = await project_service.restore_project(
            db, project_id, current_user.id
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        return project
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/{project_id}/statistics")
async def get_project_statistics(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取项目统计信息
    
    包括工作项总数、各状态数量等
    """
    try:
        statistics = await project_service.get_project_statistics(
            db, project_id
        )
        
        return statistics
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
