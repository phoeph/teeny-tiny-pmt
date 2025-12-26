"""
项目API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.project_service import project_service
from app.services.operation_log_service import operation_log_service
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, 
    ProjectListResponse, ProjectQuery
)
from app.dependencies.auth import get_current_user
from app.models import User
from app.exceptions import AppException
from app.models import OperationType, EntityType


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
        
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=OperationType.CREATE_PROJECT,
            entity_type=EntityType.PROJECT,
            entity_id=project.id,
            operation_content=f"创建项目: {project.name} (编号: {project.code})",
            result_status="success"
        )
        
        return project
    except AppException as e:
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=OperationType.CREATE_PROJECT,
            entity_type=EntityType.PROJECT,
            entity_id=0,
            operation_content=f"创建项目失败: {project_data.name}",
            result_status="failure",
            failure_reason=str(e.detail)
        )
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


@router.get("", response_model=ProjectListResponse)
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
        # 先获取旧项目数据，用于记录变更
        old_project = await project_service.get_project(db, project_id)
        if not old_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 保存旧值
        old_values = {
            'name': old_project.name,
            'description': old_project.description,
            'priority': old_project.priority,
            'status': old_project.status,
            'start_date': str(old_project.start_date) if old_project.start_date else None,
            'end_date': str(old_project.end_date) if old_project.end_date else None,
            'owner_id': old_project.owner_id,
            'creator_id': old_project.creator_id,
            'label_path': old_project.label_path,
        }
        
        # 获取旧的 owner 和 creator 用户名（用于显示）
        from sqlalchemy import select
        old_owner_name = None
        old_creator_name = None
        if old_project.owner_id:
            res = await db.execute(select(User).where(User.id == old_project.owner_id))
            u = res.scalars().first()
            if u:
                old_owner_name = u.full_name or u.username
        if old_project.creator_id:
            res = await db.execute(select(User).where(User.id == old_project.creator_id))
            u = res.scalars().first()
            if u:
                old_creator_name = u.full_name or u.username
        
        project = await project_service.update_project(
            db, project_id, project_data, current_user.id
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 获取更新的字段
        update_data = project_data.dict(exclude_unset=True)
        
        # 记录每个字段的变更
        field_logged = False
        
        # 检查 owner_id 是否变化（通过 owner_prefix/owner_email 间接修改）
        if project.owner_id != old_values.get('owner_id'):
            new_owner_name = None
            if project.owner_id:
                res = await db.execute(select(User).where(User.id == project.owner_id))
                u = res.scalars().first()
                if u:
                    new_owner_name = u.full_name or u.username
            await operation_log_service.log_field_change(
                db,
                user_id=current_user.id,
                username=current_user.username,
                entity_type=EntityType.PROJECT,
                entity_id=project.id,
                field_name='owner',
                old_value=old_owner_name,
                new_value=new_owner_name,
                operation_type=OperationType.UPDATE_PROJECT
            )
            field_logged = True
        
        # 检查 creator_id 是否变化（通过 creator_prefix/creator_email 间接修改）
        if project.creator_id != old_values.get('creator_id'):
            new_creator_name = None
            if project.creator_id:
                res = await db.execute(select(User).where(User.id == project.creator_id))
                u = res.scalars().first()
                if u:
                    new_creator_name = u.full_name or u.username
            await operation_log_service.log_field_change(
                db,
                user_id=current_user.id,
                username=current_user.username,
                entity_type=EntityType.PROJECT,
                entity_id=project.id,
                field_name='creator',
                old_value=old_creator_name,
                new_value=new_creator_name,
                operation_type=OperationType.UPDATE_PROJECT
            )
            field_logged = True
        
        for field_name, new_value in update_data.items():
            # 跳过一些特殊字段（已经通过 owner_id/creator_id 处理）
            if field_name in ('creator_prefix', 'creator_email', 'owner_prefix', 'owner_email', 'creator_id', 'owner_id'):
                continue
            
            old_value = old_values.get(field_name)
            
            # 处理日期类型
            if field_name in ('start_date', 'end_date') and new_value:
                new_value = str(new_value)
            
            # 只记录实际变更的字段
            if str(old_value) != str(new_value):
                await operation_log_service.log_field_change(
                    db,
                    user_id=current_user.id,
                    username=current_user.username,
                    entity_type=EntityType.PROJECT,
                    entity_id=project.id,
                    field_name=field_name,
                    old_value=str(old_value) if old_value is not None else None,
                    new_value=str(new_value) if new_value is not None else None,
                    operation_type=OperationType.UPDATE_PROJECT
                )
                field_logged = True
        
        # 如果没有记录任何字段变更，记录一条通用日志
        if not field_logged:
            await operation_log_service.log_operation(
                db,
                user_id=current_user.id,
                username=current_user.username,
                operation_type=OperationType.UPDATE_PROJECT,
                entity_type=EntityType.PROJECT,
                entity_id=project.id,
                operation_content=f"更新项目: {project.name} (编号: {project.code})",
                result_status="success"
            )
        
        return project
    except AppException as e:
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=OperationType.UPDATE_PROJECT,
            entity_type=EntityType.PROJECT,
            entity_id=project_id,
            operation_content=f"更新项目失败: 项目ID {project_id}",
            result_status="failure",
            failure_reason=str(e.detail)
        )
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
        
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=OperationType.DELETE_PROJECT,
            entity_type=EntityType.PROJECT,
            entity_id=project.id,
            operation_content=f"删除项目: {project.name} (编号: {project.code})",
            result_status="success"
        )
        
        return project
    except AppException as e:
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=OperationType.DELETE_PROJECT,
            entity_type=EntityType.PROJECT,
            entity_id=project_id,
            operation_content=f"删除项目失败: 项目ID {project_id}",
            result_status="failure",
            failure_reason=str(e.detail)
        )
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
