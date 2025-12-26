from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User, EntityType
from app.services.operation_log_service import operation_log_service
from pydantic import BaseModel


router = APIRouter(prefix="/api/operation-logs", tags=["操作日志"])


@router.get("/{entity_type}/{entity_id}", response_model=dict)
async def get_operation_logs(
    entity_type: str,
    entity_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        entity_type_enum = EntityType(entity_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid entity_type: {entity_type}")
    
    result = await operation_log_service.get_operation_logs(
        db,
        entity_type=entity_type_enum,
        entity_id=entity_id,
        page=page,
        page_size=page_size
    )
    
    # 获取所有用户ID，批量查询用户信息
    user_ids = list(set(log.user_id for log in result["items"] if log.user_id))
    user_map = {}
    if user_ids:
        stmt = select(User).where(User.id.in_(user_ids))
        users_result = await db.execute(stmt)
        for user in users_result.scalars().all():
            # 优先使用 full_name，没有则使用 username
            user_map[user.id] = user.full_name or user.username
    
    items = []
    for log in result["items"]:
        # 确保时间带有时区信息，如果没有则假定为 UTC
        created_at = log.created_at
        if created_at.tzinfo is None:
            from datetime import timezone
            created_at = created_at.replace(tzinfo=timezone.utc)
        
        # 获取显示名称：优先从用户表获取 full_name，否则使用日志中的 username
        display_name = user_map.get(log.user_id, log.username)
        
        items.append({
            "id": log.id,
            "user_id": log.user_id,
            "username": display_name,  # 使用显示名称
            "operation_type": log.operation_type,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "operation_content": log.operation_content,
            "field_name": log.field_name,
            "old_value": log.old_value,
            "new_value": log.new_value,
            "result_status": log.result_status,
            "failure_reason": log.failure_reason,
            "created_at": created_at.isoformat()
        })
    
    return {
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "items": items
    }