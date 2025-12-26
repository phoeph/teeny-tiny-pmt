"""
工作项API路由（任务/子任务统一模型）
"""
from typing import List, Optional, Dict, Any, Set
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import WorkItem, User
from app.dependencies.auth import get_current_user
from app.schemas.work_item import WorkItemCreate, WorkItemUpdate, WorkItemResponse, WorkItemBatchUpdateRequest
from app.services.work_item_service import work_item_service
from app.services.operation_log_service import operation_log_service
from app.models import OperationType, EntityType


router = APIRouter(prefix="/api/work-items", tags=["工作项"])


@router.get("/by-project/{project_id}")
async def list_work_items_by_project(
    project_id: int,
    include_deleted: bool = Query(False, description="是否包含已删除工作项"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    返回指定项目的任务/子任务列表（两级结构），包含计划开始/结束与状态
    """
    stmt = select(WorkItem).where(WorkItem.project_id == project_id)
    if not include_deleted:
        stmt = stmt.where(WorkItem.deleted_at.is_(None))
    result = await db.execute(stmt)
    items: List[WorkItem] = result.scalars().all()

    # 预取相关用户信息以便返回可显示的负责人/创建人前缀
    assignee_ids: Set[int] = set()
    creator_ids: Set[int] = set()
    for wi in items:
        if wi.assignee_id:
            assignee_ids.add(wi.assignee_id)
        if wi.creator_id:
            creator_ids.add(wi.creator_id)
    user_ids: Set[int] = assignee_ids.union(creator_ids)
    users_map: Dict[int, Dict[str, Any]] = {}
    if user_ids:
        users_stmt = select(User).where(User.id.in_(list(user_ids)))
        users_res = await db.execute(users_stmt)
        users: List[User] = users_res.scalars().all()
        for u in users:
            users_map[u.id] = {
                "username": u.username,
                "email_prefix": u.email_prefix,
            }

    # 构造两级结构
    jobs = [wi for wi in items if wi.kind == "JOB"]
    tasks_by_parent: Dict[int, List[WorkItem]] = {}
    for wi in items:
        if wi.kind == "TASK" and wi.parent_id:
            tasks_by_parent.setdefault(wi.parent_id, []).append(wi)

    def wi_to_dict(wi: WorkItem) -> Dict[str, Any]:
        return {
            "id": wi.id,
            "code": wi.code,
            "title": wi.title,
            "status": wi.status,
            "priority": wi.priority,
            "description": wi.description,
            "assignee_id": wi.assignee_id,
            "assignee_prefix": users_map.get(wi.assignee_id, {}).get("email_prefix"),
            "assignee_username": users_map.get(wi.assignee_id, {}).get("username"),
            "creator_id": wi.creator_id,
            "creator_prefix": users_map.get(wi.creator_id, {}).get("email_prefix"),
            "creator_username": users_map.get(wi.creator_id, {}).get("username"),
            "planned_start": wi.planned_start_date.isoformat() if wi.planned_start_date else None,
            "planned_end": wi.planned_end_date.isoformat() if wi.planned_end_date else None,
            "completed_at": wi.completed_at.isoformat() if wi.completed_at else None,
            "actual_hours": wi.actual_hours,
            "estimated_hours": wi.estimated_hours,
            "label_path": wi.label_path,
        }

    response = []
    for job in jobs:
        job_dict = wi_to_dict(job)
        children = [wi_to_dict(t) for t in tasks_by_parent.get(job.id, [])]
        job_dict["subtasks"] = children
        response.append(job_dict)

    return {"items": response}


@router.get("/{id}")
async def get_work_item_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(WorkItem).where(WorkItem.id == id, WorkItem.deleted_at.is_(None))
    res = await db.execute(stmt)
    wi: Optional[WorkItem] = res.scalars().first()
    if not wi:
        raise HTTPException(status_code=404, detail="工作项不存在")
    assignee = None
    creator = None
    if wi.assignee_id:
        res_a = await db.execute(select(User).where(User.id == wi.assignee_id))
        assignee = res_a.scalars().first()
    if wi.creator_id:
        res_c = await db.execute(select(User).where(User.id == wi.creator_id))
        creator = res_c.scalars().first()
    return {
        "id": wi.id,
        "code": wi.code,
        "kind": wi.kind,
        "project_id": wi.project_id,
        "parent_id": wi.parent_id,
        "title": wi.title,
        "status": wi.status,
        "priority": wi.priority,
        "description": wi.description,
        "assignee_id": wi.assignee_id,
        "assignee_prefix": assignee.email_prefix if assignee else None,
        "assignee_username": assignee.username if assignee else None,
        "creator_id": wi.creator_id,
        "creator_prefix": creator.email_prefix if creator else None,
        "creator_username": creator.username if creator else None,
        "planned_start_date": wi.planned_start_date,
        "planned_end_date": wi.planned_end_date,
        "completed_at": wi.completed_at,
        "actual_hours": wi.actual_hours,
        "estimated_hours": wi.estimated_hours,
        "label_path": wi.label_path,
        "created_at": wi.created_at,
        "deleted_at": wi.deleted_at,
    }


@router.get("/by-code/{code}")
async def get_work_item_by_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(WorkItem).where(WorkItem.code == code, WorkItem.deleted_at.is_(None))
    res = await db.execute(stmt)
    wi: Optional[WorkItem] = res.scalars().first()
    if not wi:
        raise HTTPException(status_code=404, detail="工作项不存在")
    assignee = None
    creator = None
    if wi.assignee_id:
        res_a = await db.execute(select(User).where(User.id == wi.assignee_id))
        assignee = res_a.scalars().first()
    if wi.creator_id:
        res_c = await db.execute(select(User).where(User.id == wi.creator_id))
        creator = res_c.scalars().first()
    return {
        "id": wi.id,
        "code": wi.code,
        "kind": wi.kind,
        "project_id": wi.project_id,
        "parent_id": wi.parent_id,
        "title": wi.title,
        "status": wi.status,
        "priority": wi.priority,
        "description": wi.description,
        "assignee_id": wi.assignee_id,
        "assignee_prefix": assignee.email_prefix if assignee else None,
        "assignee_username": assignee.username if assignee else None,
        "creator_id": wi.creator_id,
        "creator_prefix": creator.email_prefix if creator else None,
        "creator_username": creator.username if creator else None,
        "planned_start_date": wi.planned_start_date,
        "planned_end_date": wi.planned_end_date,
        "completed_at": wi.completed_at,
        "actual_hours": wi.actual_hours,
        "estimated_hours": wi.estimated_hours,
        "label_path": wi.label_path,
        "created_at": wi.created_at,
        "deleted_at": wi.deleted_at,
    }


@router.post("/", response_model=WorkItemResponse)
async def create_work_item(
    body: WorkItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        wi = await work_item_service.create(
            db,
            project_id=body.project_id,
            kind=body.kind,
            parent_id=body.parent_id,
            title=body.title,
            status=body.status,
            creator_id=current_user.id,
            planned_start_date=body.planned_start_date,
            planned_end_date=body.planned_end_date,
            description=body.description,
            assignee_id=body.assignee_id,
            assignee_prefix=body.assignee_prefix,
            assignee_email=body.assignee_email,
        )
        
        operation_type = OperationType.CREATE_JOB if body.kind == "JOB" else OperationType.CREATE_TASK
        kind_name = "作业" if body.kind == "JOB" else "任务"
        
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=operation_type,
            entity_type=EntityType.WORK_ITEM,
            entity_id=wi.id,
            operation_content=f"创建{kind_name}: {wi.title} (编号: {wi.code})",
            result_status="success"
        )
        
        return wi
    except Exception as e:
        kind_name = "作业" if body.kind == "JOB" else "任务"
        operation_type = OperationType.CREATE_JOB if body.kind == "JOB" else OperationType.CREATE_TASK
        
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=operation_type,
            entity_type=EntityType.WORK_ITEM,
            entity_id=0,
            operation_content=f"创建{kind_name}失败: {body.title}",
            result_status="failure",
            failure_reason=str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/name-exists")
async def check_name_exists(
    project_id: int = Query(..., description="项目ID"),
    type: str = Query(..., pattern="^(job|task)$", description="类型：job或task"),
    title: str = Query(..., min_length=1, max_length=500, description="标题"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    kind = 'JOB' if type.lower() == 'job' else 'TASK'
    stmt = select(WorkItem).where(
        WorkItem.project_id == project_id,
        WorkItem.kind == kind,
        WorkItem.title == title,
        WorkItem.deleted_at.is_(None)
    )
    res = await db.execute(stmt)
    wi = res.scalars().first()
    return {"exists": wi is not None, "conflict_id": wi.id if wi else None}


@router.patch("/batch")
async def batch_update_work_items(
    body: WorkItemBatchUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    批量更新工作项，保证在一个事务中全部成功或全部失败。
    返回已更新的工作项列表（扁平），前端可据此合并本地缓存。
    """
    updated = []
    try:
        if db.in_transaction():
            async with db.begin_nested():
                for item in body.items:
                    wi = await work_item_service.update(
                        db,
                        id=item.id,
                        data={k: v for k, v in item.dict(exclude_unset=True).items() if k != 'id'},
                        current_user_id=current_user.id,
                    )
                    if not wi:
                        raise HTTPException(status_code=404, detail=f"工作项不存在: {item.id}")
                    updated.append(wi)
        else:
            async with db.begin():
                for item in body.items:
                    wi = await work_item_service.update(
                        db,
                        id=item.id,
                        data={k: v for k, v in item.dict(exclude_unset=True).items() if k != 'id'},
                        current_user_id=current_user.id,
                    )
                    if not wi:
                        raise HTTPException(status_code=404, detail=f"工作项不存在: {item.id}")
                    updated.append(wi)
        return {"items": [
            {
                "id": wi.id,
                "code": wi.code,
                "kind": wi.kind,
                "project_id": wi.project_id,
                "parent_id": wi.parent_id,
                "title": wi.title,
                "status": wi.status,
                "priority": wi.priority,
                "assignee_id": wi.assignee_id,
                "planned_start_date": wi.planned_start_date,
                "planned_end_date": wi.planned_end_date,
                "completed_at": wi.completed_at,
                "actual_hours": wi.actual_hours,
                "label_path": wi.label_path,
                "created_at": wi.created_at,
                "deleted_at": wi.deleted_at,
            } for wi in updated
        ]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{id}", response_model=WorkItemResponse)
async def update_work_item(
    id: int,
    body: WorkItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 先获取旧数据，用于记录变更
        old_wi = await work_item_service.get(db, id=id)
        if not old_wi:
            raise HTTPException(status_code=404, detail="工作项不存在")
        
        # 保存旧值
        old_values = {
            'title': old_wi.title,
            'description': old_wi.description,
            'status': old_wi.status,
            'priority': old_wi.priority,
            'assignee_id': old_wi.assignee_id,
            'planned_start_date': str(old_wi.planned_start_date) if old_wi.planned_start_date else None,
            'planned_end_date': str(old_wi.planned_end_date) if old_wi.planned_end_date else None,
            'actual_hours': old_wi.actual_hours,
            'label_path': old_wi.label_path,
        }
        
        wi = await work_item_service.update(db, id=id, data=body.dict(exclude_unset=True), current_user_id=current_user.id)
        if not wi:
            raise HTTPException(status_code=404, detail="工作项不存在")
        
        kind_name = "作业" if wi.kind == "JOB" else "任务"
        operation_type = OperationType.UPDATE_JOB if wi.kind == "JOB" else OperationType.UPDATE_TASK
        
        # 获取更新的字段
        update_data = body.dict(exclude_unset=True)
        
        # 记录每个字段的变更
        field_logged = False
        for field_name, new_value in update_data.items():
            old_value = old_values.get(field_name)
            
            # 处理日期类型
            if field_name in ('planned_start_date', 'planned_end_date') and new_value:
                new_value = str(new_value)
            
            # 只记录实际变更的字段
            if str(old_value) != str(new_value):
                await operation_log_service.log_field_change(
                    db,
                    user_id=current_user.id,
                    username=current_user.username,
                    entity_type=EntityType.WORK_ITEM,
                    entity_id=wi.id,
                    field_name=field_name,
                    old_value=str(old_value) if old_value is not None else None,
                    new_value=str(new_value) if new_value is not None else None,
                    operation_type=operation_type
                )
                field_logged = True
        
        # 如果没有记录任何字段变更，记录一条通用日志
        if not field_logged:
            await operation_log_service.log_operation(
                db,
                user_id=current_user.id,
                username=current_user.username,
                operation_type=operation_type,
                entity_type=EntityType.WORK_ITEM,
                entity_id=wi.id,
                operation_content=f"更新{kind_name}: {wi.title} (编号: {wi.code})",
                result_status="success"
            )
        
        return wi
    except HTTPException as e:
        raise e
    except Exception as e:
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=OperationType.UPDATE_TASK,
            entity_type=EntityType.WORK_ITEM,
            entity_id=id,
            operation_content=f"更新工作项失败: ID {id}",
            result_status="failure",
            failure_reason=str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))


class CascadeStatusRequest(BaseModel):
    status: str
    completed_at: Optional[datetime] = None
    actual_hours: Optional[float] = None


@router.post("/{id}/cascade-status")
async def cascade_status(
    id: int,
    body: CascadeStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        async with db.begin():
            updated = await work_item_service.cascade_status(
                db,
                job_id=id,
                target_status=body.status,
                current_user_id=current_user.id,
                completed_at=body.completed_at,
                actual_hours=body.actual_hours,
            )
        return {"items": [
            {
                "id": wi.id,
                "code": wi.code,
                "kind": wi.kind,
                "project_id": wi.project_id,
                "parent_id": wi.parent_id,
                "title": wi.title,
                "status": wi.status,
                "assignee_id": wi.assignee_id,
                "planned_start_date": wi.planned_start_date,
                "planned_end_date": wi.planned_end_date,
                "completed_at": wi.completed_at,
                "actual_hours": wi.actual_hours,
                "created_at": wi.created_at,
                "deleted_at": wi.deleted_at,
            } for wi in updated
        ]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}", response_model=WorkItemResponse)
async def delete_work_item(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        wi = await work_item_service.soft_delete(db, id=id, current_user_id=current_user.id)
        if not wi:
            raise HTTPException(status_code=404, detail="工作项不存在")
        
        kind_name = "作业" if wi.kind == "JOB" else "任务"
        operation_type = OperationType.DELETE_JOB if wi.kind == "JOB" else OperationType.DELETE_TASK
        
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=operation_type,
            entity_type=EntityType.WORK_ITEM,
            entity_id=wi.id,
            operation_content=f"删除{kind_name}: {wi.title} (编号: {wi.code})",
            result_status="success"
        )
        
        return wi
    except HTTPException as e:
        raise e
    except Exception as e:
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=OperationType.DELETE_TASK,
            entity_type=EntityType.WORK_ITEM,
            entity_id=id,
            operation_content=f"删除工作项失败: ID {id}",
            result_status="failure",
            failure_reason=str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))
