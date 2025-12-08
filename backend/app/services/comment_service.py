import re
from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Comment, Mention, User, Notification, Project, WorkItem
from app.exceptions import NotFoundException, ForbiddenException
from app.utils.html import sanitize_html


MENTION_PATTERN = re.compile(r"@([\w\u4e00-\u9fa5]+)")


class CommentService:
    async def add_comment(self, session: AsyncSession, *, entity_type: str, entity_id: int, author_id: int, content: str) -> Comment:
        # 只读校验（项目归档时禁止）
        if entity_type == 'project':
            project = await session.get(Project, entity_id)
            if not project:
                raise NotFoundException('项目不存在')
            if project.archived:
                raise ForbiddenException('项目已归档，禁止写操作')
        elif entity_type == 'work_item':
            wi = await session.get(WorkItem, entity_id)
            if not wi:
                raise NotFoundException('工作项不存在')
            project = await session.get(Project, wi.project_id)
            if project.archived:
                raise ForbiddenException('项目已归档，禁止写操作')

        c = Comment(entity_type=entity_type, entity_id=entity_id, author_id=author_id, content=sanitize_html(content))
        session.add(c)
        await session.flush()
        await session.refresh(c)

        # 解析@并生成提及与通知（去重）
        mentioned_ids = set()
        for m in MENTION_PATTERN.findall(content or ''):
            stmt = select(User).where((User.username == m) | (User.email_prefix == m) | (User.full_name == m))
            result = await session.execute(stmt)
            for u in result.scalars().all():
                mentioned_ids.add(u.id)
        url_anchor = f"comment-{c.id}"
        if entity_type == 'project':
            url_anchor = f"project?id={entity_id}#comment-{c.id}"
        elif entity_type == 'work_item':
            wi = await session.get(WorkItem, entity_id)
            if wi:
                if wi.kind == 'JOB':
                    url_anchor = f"job?code={wi.code}&project={wi.project_id}#comment-{c.id}"
                elif wi.kind == 'TASK':
                    parent = await session.get(WorkItem, wi.parent_id) if wi.parent_id else None
                    job_code = parent.code if parent else ''
                    url_anchor = f"task?code={wi.code}&project={wi.project_id}&job={job_code}#comment-{c.id}"
        for uid in mentioned_ids:
            mention = Mention(comment_id=c.id, mentioned_user_id=uid, anchor=f"comment-{c.id}")
            session.add(mention)
            notif = Notification(user_id=uid, type='comment_mention', title='被@提醒', content=content, target_type='comment', target_id=c.id, anchor=url_anchor)
            session.add(notif)
        await session.flush()
        return c

    async def list_comments(self, session: AsyncSession, *, entity_type: str, entity_id: int) -> List[Comment]:
        stmt = select(Comment).where(Comment.entity_type == entity_type, Comment.entity_id == entity_id, Comment.deleted_at.is_(None)).order_by(Comment.created_at.asc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def edit_comment(self, session: AsyncSession, *, id: int, content: str) -> Comment:
        c = await session.get(Comment, id)
        if not c or c.deleted_at is not None:
            raise NotFoundException('评论不存在')
        c.content = sanitize_html(content)
        c.updated_at = datetime.utcnow()
        await session.flush()
        await session.refresh(c)
        return c

    async def delete_comment(self, session: AsyncSession, *, id: int) -> Comment:
        c = await session.get(Comment, id)
        if not c or c.deleted_at is not None:
            raise NotFoundException('评论不存在')
        c.deleted_at = datetime.utcnow()
        await session.flush()
        await session.refresh(c)
        return c

    async def resolve_comment_url(self, session: AsyncSession, *, id: int) -> str:
        c = await session.get(Comment, id)
        if not c or c.deleted_at is not None:
            raise NotFoundException('评论不存在')
        base = ''
        if c.entity_type == 'project':
            base = f"project?id={c.entity_id}"
        elif c.entity_type == 'work_item':
            wi = await session.get(WorkItem, c.entity_id)
            if wi:
                if wi.kind == 'JOB':
                    base = f"job?code={wi.code}&project={wi.project_id}"
                elif wi.kind == 'TASK':
                    parent = await session.get(WorkItem, wi.parent_id) if wi.parent_id else None
                    job_code = parent.code if parent else ''
                    base = f"task?code={wi.code}&project={wi.project_id}&job={job_code}"
        return f"{base}#comment-{c.id}"


comment_service = CommentService()
