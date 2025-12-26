from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User, Watch, OperationType, EntityType
from app.services.operation_log_service import operation_log_service

router = APIRouter(prefix="/api/watch", tags=["关注"])

@router.get("/{entity_type}/{entity_id}")
async def list_watchers(entity_type: str, entity_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Watch).where(Watch.entity_type == entity_type, Watch.entity_id == entity_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    users_stmt = select(User).where(User.id.in_([w.user_id for w in items]))
    users_res = await db.execute(users_stmt)
    users = users_res.scalars().all()
    return [{"id": u.id, "username": u.username, "email_prefix": u.email_prefix} for u in users]

@router.post("/")
async def watch(entity_type: str, entity_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    w = Watch(entity_type=entity_type, entity_id=entity_id, user_id=current_user.id)
    db.add(w)
    try:
        await db.flush()
        
        # 记录操作日志
        log_entity_type = EntityType.WORK_ITEM if entity_type == "work_item" else EntityType.PROJECT
        await operation_log_service.log_operation(
            session=db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=OperationType.START_WATCHING,
            entity_type=log_entity_type,
            entity_id=entity_id,
            operation_content=f"开始关注"
        )
        
        await db.commit()
        return {"ok": True}
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="已关注或参数错误")

@router.delete("/")
async def unwatch(entity_type: str, entity_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = delete(Watch).where(Watch.entity_type == entity_type, Watch.entity_id == entity_id, Watch.user_id == current_user.id)
    await db.execute(stmt)
    
    # 记录操作日志
    log_entity_type = EntityType.WORK_ITEM if entity_type == "work_item" else EntityType.PROJECT
    await operation_log_service.log_operation(
        session=db,
        user_id=current_user.id,
        username=current_user.username,
        operation_type=OperationType.STOP_WATCHING,
        entity_type=log_entity_type,
        entity_id=entity_id,
        operation_content=f"取消关注"
    )
    
    await db.commit()
    return {"ok": True}
