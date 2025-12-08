from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import WorkItem, Project, User, AuditLog
from app.utils.worktime import compute_estimated_hours, compute_actual_hours
from app.utils.timezone import now_cst
from app.services.sequence_service import sequence_service
from app.exceptions import ValidationException, NotFoundException, ForbiddenException
from app.utils.html import sanitize_html


class WorkItemService:
    async def create(self, session: AsyncSession, *, project_id: int, kind: str, parent_id: Optional[int], title: str, status: str, creator_id: int, planned_start_date, planned_end_date, description: Optional[str] = None) -> WorkItem:
        project = await session.get(Project, project_id)
        if not project or project.deleted_at is not None:
            raise NotFoundException("项目不存在")
        if project.archived:
            raise ForbiddenException("项目已归档，禁止写操作")

        if kind == 'TASK' and not parent_id:
            raise ValidationException("TASK必须指定parent_id")
        if kind == 'JOB' and parent_id is not None:
            raise ValidationException("JOB禁止指定parent_id")

        # 基本日期序关系校验
        if planned_start_date and planned_end_date and planned_end_date < planned_start_date:
            raise ValidationException("计划结束日期不得早于开始日期")

        # 父子范围校验：TASK必须落入父任务的计划范围（若父已设置范围）
        if kind == 'TASK' and parent_id:
            parent = await session.get(WorkItem, parent_id)
            if not parent or parent.deleted_at is not None:
                raise NotFoundException("父任务不存在")
            if parent.planned_start_date and parent.planned_end_date and planned_start_date and planned_end_date:
                if planned_start_date < parent.planned_start_date or planned_end_date > parent.planned_end_date:
                    raise ValidationException("子任务计划区间必须落入父任务计划范围")

        # 唯一性：项目维度同名JOB不可重复
        if kind == 'JOB':
            res = await session.execute(select(WorkItem).where(
                WorkItem.project_id == project_id,
                WorkItem.kind == 'JOB',
                WorkItem.title == title,
                WorkItem.deleted_at.is_(None)
            ))
            exist = res.scalars().first()
            if exist:
                raise ValidationException("JOB名称在项目内必须唯一")

        code = await sequence_service.generate_code(session, 'JOB' if kind == 'JOB' else 'TASK')
        from app.utils.html import sanitize_html
        est_hours = compute_estimated_hours(planned_start_date, planned_end_date)
        wi = WorkItem(
            code=code,
            kind=kind,
            project_id=project_id,
            parent_id=parent_id,
            title=title,
            status=status,
            planned_start_date=planned_start_date,
            planned_end_date=planned_end_date,
            creator_id=creator_id,
            description=sanitize_html(description) if description else None,
            estimated_hours=est_hours if est_hours > 0 else None,
        )
        session.add(wi)
        await session.flush()
        await session.refresh(wi)
        return wi

    async def update(self, session: AsyncSession, *, id: int, data: dict, current_user_id: int) -> Optional[WorkItem]:
        wi = await session.get(WorkItem, id)
        if not wi or wi.deleted_at is not None:
            return None
        project = await session.get(Project, wi.project_id)
        if project.archived:
            raise ForbiddenException("项目已归档，禁止写操作")

        # 状态流转与完成态校验
        new_status = data.get('status')
        if new_status == 'done':
            data.setdefault('assignee_id', current_user_id)
            data['completed_at'] = data.get('completed_at') or now_cst()
            start_for_actual = wi.start_date or wi.planned_start_date
            data['actual_hours'] = compute_actual_hours(start_for_actual, data['completed_at'])
        elif new_status in ('todo','doing') and wi.status == 'done':
            data['completed_at'] = None
            data['actual_hours'] = None

        # 负责人解析：优先 assignee_id，其次 assignee_prefix/assignee_email
        assignee_prefix = data.pop("assignee_prefix", None)
        assignee_email = data.pop("assignee_email", None)
        if not data.get("assignee_id"):
            lookup_prefix = None
            if assignee_prefix:
                lookup_prefix = assignee_prefix.strip()
            elif assignee_email:
                # 取邮箱前缀部分
                p = assignee_email.strip()
                if "@" in p:
                    lookup_prefix = p.split("@", 1)[0]
                else:
                    lookup_prefix = p
            if lookup_prefix:
                res = await session.execute(select(User).where(User.email_prefix == lookup_prefix))
                user = res.scalars().first()
                if user:
                    data["assignee_id"] = user.id

        # Reporter(创建人)解析：优先 creator_id，其次 creator_prefix/creator_email
        creator_prefix = data.pop("creator_prefix", None)
        creator_email = data.pop("creator_email", None)
        if not data.get("creator_id"):
            c_lookup = None
            if creator_prefix:
                c_lookup = creator_prefix.strip()
            elif creator_email:
                cp = creator_email.strip()
                if "@" in cp:
                    c_lookup = cp.split("@", 1)[0]
                else:
                    c_lookup = cp
            if c_lookup:
                res2 = await session.execute(select(User).where(User.email_prefix == c_lookup))
                cuser = res2.scalars().first()
                if cuser:
                    data["creator_id"] = cuser.id

        # 计划日期更新的基本校验与父子范围约束
        new_start = data.get('planned_start_date', wi.planned_start_date)
        new_end = data.get('planned_end_date', wi.planned_end_date)
        if new_start and new_end and new_end < new_start:
            raise ValidationException("计划结束日期不得早于开始日期")

        if wi.kind == 'TASK':
            if wi.parent_id:
                parent = await session.get(WorkItem, wi.parent_id)
                if not parent or parent.deleted_at is not None:
                    raise NotFoundException("父任务不存在")
                # 若父任务已设置计划范围，则子任务必须落入其中（要求子任务同时具备开始/结束计划）
                if parent.planned_start_date and parent.planned_end_date and new_start and new_end:
                    if new_start < parent.planned_start_date or new_end > parent.planned_end_date:
                        raise ValidationException("子任务计划区间必须落入父任务计划范围")
        else:  # JOB
            # 若存在子任务计划范围，则父任务的计划必须覆盖所有子任务
            # 仅在父有新计划（或已有计划）且子任务存在有效计划时进行校验
            if new_start and new_end:
                res = await session.execute(select(WorkItem).where(WorkItem.parent_id == wi.id, WorkItem.deleted_at.is_(None)))
                children = res.scalars().all()
                if children:
                    # 计算子任务的最小开始与最大结束（仅考虑有计划日期的子任务）
                    child_starts = [c.planned_start_date for c in children if c.planned_start_date]
                    child_ends = [c.planned_end_date for c in children if c.planned_end_date]
                    if child_starts and child_ends:
                        min_child_start = min(child_starts)
                        max_child_end = max(child_ends)
                        if new_start > min_child_start or new_end < max_child_end:
                            raise ValidationException("父任务计划范围必须覆盖所有子任务的计划区间")

        # 描述编辑权限：仅 Reporter 或 demo/admin 可编辑
        if 'description' in data:
            can = False
            if current_user_id == wi.creator_id:
                can = True
            else:
                resu = await session.execute(select(User).where(User.id == current_user_id))
                cu = resu.scalars().first()
                if cu and cu.username in ('demo', 'admin'):
                    can = True
            if not can:
                raise ForbiddenException("仅创建人或管理员可编辑描述")
            data['description'] = sanitize_html(data['description']) if data['description'] is not None else None

        old_status = wi.status
        # 若计划开始/结束发生变化，更新预估工时
        if ('planned_start_date' in data) or ('planned_end_date' in data):
            est = compute_estimated_hours(new_start, new_end)
            data['estimated_hours'] = est if est > 0 else None
        # 若进入完成态且未设置预估工时，补算一次
        if (new_status == 'done') and not data.get('estimated_hours'):
            est = compute_estimated_hours(new_start, new_end)
            data['estimated_hours'] = est if est > 0 else None

        for k, v in data.items():
            setattr(wi, k, v)
        await session.flush()
        await session.refresh(wi)
        if 'status' in data and old_status != wi.status:
            al = AuditLog(entity_type='work_item', entity_id=wi.id, action='status_change', old_value=old_status, new_value=wi.status, user_id=current_user_id)
            session.add(al)
        if wi.kind == 'TASK' and 'status' in data and wi.parent_id:
            res = await session.execute(select(WorkItem).where(WorkItem.parent_id == wi.parent_id, WorkItem.deleted_at.is_(None)))
            siblings = res.scalars().all()
            if siblings:
                statuses = {s.status for s in siblings}
                if len(statuses) == 1:
                    target = list(statuses)[0]
                    parent = await session.get(WorkItem, wi.parent_id)
                    if parent and parent.kind == 'JOB':
                        parent_old = parent.status
                        parent.status = target
                        if target == 'done' and not parent.completed_at:
                            parent.completed_at = now_cst()
                            parent.actual_hours = parent.actual_hours or compute_actual_hours(parent.start_date or parent.planned_start_date, parent.completed_at)
                            parent.estimated_hours = compute_estimated_hours(parent.planned_start_date, parent.planned_end_date) or parent.estimated_hours
                        elif target in ('todo','doing') and parent_old == 'done':
                            parent.completed_at = None
                            parent.actual_hours = None
                        await session.flush()
                        await session.refresh(parent)
                        al2 = AuditLog(entity_type='work_item', entity_id=parent.id, action='status_sync', old_value=parent_old, new_value=parent.status, user_id=current_user_id)
                        session.add(al2)
        return wi

    async def cascade_status(self, session: AsyncSession, *, job_id: int, target_status: str, current_user_id: int, completed_at: Optional[datetime] = None, actual_hours: Optional[float] = None) -> list[WorkItem]:
        job = await session.get(WorkItem, job_id)
        if not job or job.kind != 'JOB' or job.deleted_at is not None:
            raise NotFoundException("工作项不存在或不是JOB")
        project = await session.get(Project, job.project_id)
        if project.archived:
            raise ForbiddenException("项目已归档，禁止写操作")
        res = await session.execute(select(WorkItem).where(WorkItem.parent_id == job.id, WorkItem.deleted_at.is_(None)))
        tasks = res.scalars().all()
        updated = []
        async with session.begin_nested():
            prev_job_status = job.status
            job.status = target_status
            if target_status == 'done':
                job.completed_at = completed_at or now_cst()
                job.actual_hours = compute_actual_hours(job.start_date or job.planned_start_date, job.completed_at)
                job.estimated_hours = compute_estimated_hours(job.planned_start_date, job.planned_end_date) or job.estimated_hours
            else:
                job.completed_at = None
                job.actual_hours = None
            await session.flush()
            await session.refresh(job)
            updated.append(job)
            session.add(AuditLog(entity_type='work_item', entity_id=job.id, action='status_cascade', old_value=prev_job_status, new_value=job.status, user_id=current_user_id))
            for t in tasks:
                prev = t.status
                t.status = target_status
                if target_status == 'done':
                    t.completed_at = completed_at or now_cst()
                    t.actual_hours = compute_actual_hours(t.start_date or t.planned_start_date, t.completed_at)
                    t.estimated_hours = compute_estimated_hours(t.planned_start_date, t.planned_end_date) or t.estimated_hours
                else:
                    t.completed_at = None
                    t.actual_hours = None
                await session.flush()
                await session.refresh(t)
                updated.append(t)
                session.add(AuditLog(entity_type='work_item', entity_id=t.id, action='status_cascade', old_value=prev, new_value=t.status, user_id=current_user_id))
        return updated

    async def soft_delete(self, session: AsyncSession, *, id: int, current_user_id: int) -> Optional[WorkItem]:
        wi = await session.get(WorkItem, id)
        if not wi or wi.deleted_at is not None:
            return None
        project = await session.get(Project, wi.project_id)
        if project.archived:
            raise ForbiddenException("项目已归档，禁止写操作")
        wi.deleted_at = datetime.utcnow()
        await session.flush()
        await session.refresh(wi)
        return wi


work_item_service = WorkItemService()
