from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import Attachment, Comment, User
from app.config import ATTACHMENTS_DIR, ALLOWED_MIME_TYPES, MAX_ATTACHMENT_SIZE


router = APIRouter(prefix="/api/attachments", tags=["附件"])


@router.post("/comments/{comment_id}")
async def upload_attachment(comment_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    c = await db.get(Comment, comment_id)
    if not c:
        raise HTTPException(status_code=404, detail="评论不存在")
    data = await file.read()
    if len(data) > MAX_ATTACHMENT_SIZE:
        raise HTTPException(status_code=400, detail="附件大小超限")
    mime = file.content_type or 'application/octet-stream'
    if mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="附件类型不允许")
    ext = ALLOWED_MIME_TYPES[mime]
    target = ATTACHMENTS_DIR / f"c{comment_id}_{file.filename}"
    Path(target).write_bytes(data)
    att = Attachment(comment_id=comment_id, file_path=str(target), original_filename=file.filename, file_size=len(data), mime_type=mime, uploaded_by_id=current_user.id)
    db.add(att)
    await db.flush()
    return {"id": att.id}


@router.get("/comments/{comment_id}")
async def list_attachments(comment_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Attachment).where(Attachment.comment_id == comment_id))
    items = result.scalars().all()
    return [{"id": a.id, "file_name": a.original_filename, "size": a.file_size, "mime": a.mime_type} for a in items]


@router.get("/{id}")
async def download_attachment(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    a = await db.get(Attachment, id)
    if not a:
        raise HTTPException(status_code=404, detail="附件不存在")
    return FileResponse(a.file_path, media_type=a.mime_type, filename=a.original_filename)
