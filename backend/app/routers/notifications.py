from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import Notification, User


router = APIRouter(prefix="/api/notifications", tags=["通知"])


@router.get("/")
async def list_notifications(
    unread: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    base = select(Notification).where(Notification.user_id == current_user.id)
    if unread:
        base = base.where(Notification.is_read == False)
    # total count
    from sqlalchemy import func
    total_q = await db.execute(select(func.count()).select_from(base.subquery()))
    total = int(total_q.scalar() or 0)
    # page data (order by created_at desc)
    stmt = base.order_by(Notification.created_at.desc()).offset((page-1)*page_size).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": [{"id": n.id, "title": n.title, "content": n.content, "anchor": n.anchor, "read": n.is_read, "created_at": n.created_at.isoformat() if n.created_at else None, "target_type": n.target_type, "target_id": n.target_id} for n in items]
    }


@router.patch("/{id}")
async def mark_read(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    n = await db.get(Notification, id)
    if n and n.user_id == current_user.id:
        n.is_read = True
        await db.flush()
    return {"id": id}
