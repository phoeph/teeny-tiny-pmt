from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User, Comment, OperationType, EntityType
from app.services.comment_service import comment_service
from app.services.operation_log_service import operation_log_service
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/comments", tags=["评论"])


class CommentCreate(BaseModel):
    entity_type: str = Field(..., pattern="^(project|work_item)$")
    entity_id: int
    content: str


class CommentEdit(BaseModel):
    content: str


@router.post("/", response_model=dict)
async def create_comment(body: CommentCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        c = await comment_service.add_comment(db, entity_type=body.entity_type, entity_id=body.entity_id, author_id=current_user.id, content=body.content)
        
        target_entity_type = EntityType.PROJECT if body.entity_type == 'project' else EntityType.WORK_ITEM
        
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=OperationType.ADD_COMMENT,
            entity_type=target_entity_type,
            entity_id=body.entity_id,
            operation_content=f"添加评论: {body.content[:50]}{'...' if len(body.content) > 50 else ''}",
            result_status="success"
        )
        
        return {"id": c.id}
    except Exception as e:
        target_entity_type = EntityType.PROJECT if body.entity_type == 'project' else EntityType.WORK_ITEM
        
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=OperationType.ADD_COMMENT,
            entity_type=target_entity_type,
            entity_id=body.entity_id,
            operation_content=f"添加评论失败",
            result_status="failure",
            failure_reason=str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{entity_type}/{entity_id}", response_model=list[dict])
async def list_comments(entity_type: str, entity_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = await comment_service.list_comments(db, entity_type=entity_type, entity_id=entity_id)
    result: list[dict] = []
    for c in items:
        author: User | None = await db.get(User, c.author_id)
        result.append({
            "id": c.id,
            "author_id": c.author_id,
            "author": {
                "id": author.id if author else c.author_id,
                "username": author.username if author else None,
                "email_prefix": author.email_prefix if author else None,
                "full_name": author.full_name if author else None,
            },
            "content": c.content,
            "created_at": c.created_at.isoformat()
        })
    return result


@router.patch("/{id}", response_model=dict)
async def edit_comment(id: int, body: CommentEdit, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        c = await comment_service.edit_comment(db, id=id, content=body.content)
        
        target_entity_type = EntityType.PROJECT if c.entity_type == 'project' else EntityType.WORK_ITEM
        
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=OperationType.UPDATE_COMMENT,
            entity_type=target_entity_type,
            entity_id=c.entity_id,
            operation_content=f"更新评论: {body.content[:50]}{'...' if len(body.content) > 50 else ''}",
            result_status="success"
        )
        
        return {"id": c.id}
    except Exception as e:
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=OperationType.UPDATE_COMMENT,
            entity_type=EntityType.WORK_ITEM,
            entity_id=0,
            operation_content=f"更新评论失败",
            result_status="failure",
            failure_reason=str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}", response_model=dict)
async def delete_comment(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        c = await comment_service.delete_comment(db, id=id)
        
        target_entity_type = EntityType.PROJECT if c.entity_type == 'project' else EntityType.WORK_ITEM
        
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=OperationType.DELETE_COMMENT,
            entity_type=target_entity_type,
            entity_id=c.entity_id,
            operation_content=f"删除评论: ID {c.id}",
            result_status="success"
        )
        
        return {"id": c.id}
    except Exception as e:
        await operation_log_service.log_operation(
            db,
            user_id=current_user.id,
            username=current_user.username,
            operation_type=OperationType.DELETE_COMMENT,
            entity_type=EntityType.WORK_ITEM,
            entity_id=0,
            operation_content=f"删除评论失败",
            result_status="failure",
            failure_reason=str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/context/{id}", response_model=dict)
async def resolve_comment_context(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        url = await comment_service.resolve_comment_url(db, id=id)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
