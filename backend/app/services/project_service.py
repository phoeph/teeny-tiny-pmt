"""
项目服务 - 处理项目相关的业务逻辑
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from app.models import Project, User, WorkItem
from app.utils.html import sanitize_html
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectQuery
from app.services.sequence_service import sequence_service
from app.exceptions import AppException, NotFoundException, ForbiddenException, ValidationException


class ProjectService:
    """项目服务"""
    
    async def create_project(
        self, 
        session: AsyncSession, 
        project_data: ProjectCreate, 
        owner_id: int
    ) -> Project:
        """
        创建新项目
        
        Args:
            session: 数据库会话
            project_data: 项目创建数据
            owner_id: 所有者ID
            
        Returns:
            创建的项目对象
        """
        # 生成项目编号
        code = await sequence_service.generate_code(session, "PRO")
        
        # 创建项目
        project = Project(
            code=code,
            name=project_data.name,
            description=project_data.description,
            creator_id=owner_id,
            owner_id=owner_id,
            priority="medium",
            start_date=project_data.start_date,
            end_date=project_data.end_date,
            status="active",
            archived=False
        )
        
        session.add(project)
        await session.flush()  # 获取ID
        await session.refresh(project)
        
        return project
    
    async def get_project(
        self, 
        session: AsyncSession, 
        project_id: int, 
        include_deleted: bool = False
    ) -> Optional[Project]:
        """
        获取项目详情
        
        Args:
            session: 数据库会话
            project_id: 项目ID
            include_deleted: 是否包含已删除的项目
            
        Returns:
            项目对象，如果不存在返回None
        """
        stmt = select(Project).where(Project.id == project_id)
        
        if not include_deleted:
            stmt = stmt.where(Project.deleted_at.is_(None))
        
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_project_by_code(
        self, 
        session: AsyncSession, 
        code: str, 
        include_deleted: bool = False
    ) -> Optional[Project]:
        """
        根据项目编号获取项目
        
        Args:
            session: 数据库会话
            code: 项目编号
            include_deleted: 是否包含已删除的项目
            
        Returns:
            项目对象，如果不存在返回None
        """
        stmt = select(Project).where(Project.code == code)
        
        if not include_deleted:
            stmt = stmt.where(Project.deleted_at.is_(None))
        
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_projects(
        self, 
        session: AsyncSession, 
        query: ProjectQuery,
        current_user_id: Optional[int] = None
    ) -> Tuple[List[Project], int]:
        """
        获取项目列表
        
        Args:
            session: 数据库会话
            query: 查询参数
            current_user_id: 当前用户ID（用于权限控制）
            
        Returns:
            (项目列表, 总数量) 元组
        """
        # 基础查询
        stmt = select(Project)
        
        # 过滤条件
        conditions = []
        
        # 状态筛选
        if query.status:
            conditions.append(Project.status == query.status)
        
        # 归档状态筛选
        if query.archived is not None:
            conditions.append(Project.archived == query.archived)
        
        # 是否包含已删除的项目
        if not query.include_deleted:
            conditions.append(Project.deleted_at.is_(None))
        
        # 搜索功能
        if query.search:
            search_term = f"%{query.search}%"
            conditions.append(
                or_(
                    Project.name.like(search_term),
                    Project.description.like(search_term)
                )
            )
        
        # 应用过滤条件
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        # 获取总数量
        count_stmt = select(func.count()).select_from(Project)
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        
        total_result = await session.execute(count_stmt)
        total = total_result.scalar()
        
        # 分页
        offset = (query.page - 1) * query.size
        stmt = stmt.offset(offset).limit(query.size)
        
        # 按创建时间倒序排列
        stmt = stmt.order_by(Project.created_at.desc())
        
        result = await session.execute(stmt)
        projects = result.scalars().all()
        
        return list(projects), total
    
    async def update_project(
        self, 
        session: AsyncSession, 
        project_id: int, 
        project_data: ProjectUpdate,
        current_user_id: int
    ) -> Optional[Project]:
        """
        更新项目
        
        Args:
            session: 数据库会话
            project_id: 项目ID
            project_data: 更新数据
            current_user_id: 当前用户ID（用于权限验证）
            
        Returns:
            更新后的项目对象，如果不存在返回None
        """
        project = await self.get_project(session, project_id)
        if not project:
            return None
        
        update_data = project_data.dict(exclude_unset=True)
        # 描述单独权限控制：Reporter或demo/admin可编辑；其他字段仍需所有者权限
        resu = await session.execute(select(User).where(User.id == current_user_id))
        cu = resu.scalars().first()
        is_admin = bool(cu and cu.username in ("demo", "admin"))
        wants_only_desc = set(update_data.keys()) == {"description"}
        wants_only_priority = set(update_data.keys()) == {"priority"}
        wants_only_label = set(update_data.keys()) == {"label_path"}
        reporter_fields = {"creator_id","creator_prefix","creator_email"}
        owner_fields = {"owner_id","owner_prefix","owner_email"}
        wants_only_reporter = set(update_data.keys()).issubset(reporter_fields) and len(update_data.keys())>0
        wants_only_owner = set(update_data.keys()).issubset(owner_fields) and len(update_data.keys())>0
        if wants_only_desc or wants_only_priority or wants_only_label:
            if not (is_admin or current_user_id == project.creator_id):
                if not (current_user_id == project.owner_id):
                    raise ForbiddenException("仅创建人、管理员或项目所有者可编辑")
        elif wants_only_reporter:
            # 允许管理员或当前Reporter更新Reporter
            if not (is_admin or current_user_id == project.creator_id):
                raise ForbiddenException("仅创建人或管理员可更新Reporter")
        elif wants_only_owner:
            # 允许任何登录用户更新项目Assignee/Owner
            pass
        else:
            if project.owner_id != current_user_id:
                raise ForbiddenException("只有项目所有者可以更新项目")
        
        # 检查项目是否已归档
        if project.archived:
            raise ValidationException("已归档的项目不能修改")
        
        # 更新字段
        # Reporter解析：优先 creator_id，其次 creator_prefix/creator_email
        creator_id = update_data.pop("creator_id", None)
        creator_prefix = update_data.pop("creator_prefix", None)
        creator_email = update_data.pop("creator_email", None)
        if creator_id:
            project.creator_id = creator_id
        else:
            lookup = None
            if creator_prefix:
                lookup = creator_prefix.strip()
            elif creator_email:
                cp = creator_email.strip()
                lookup = cp.split("@", 1)[0] if "@" in cp else cp
            if lookup:
                res = await session.execute(select(User).where(User.email_prefix == lookup))
                u = res.scalars().first()
                if u:
                    project.creator_id = u.id
        # Owner解析：优先 owner_id，其次 owner_prefix/owner_email
        owner_id = update_data.pop("owner_id", None)
        owner_prefix = update_data.pop("owner_prefix", None)
        owner_email = update_data.pop("owner_email", None)
        if owner_id:
            project.owner_id = owner_id
        else:
            o_lookup = None
            if owner_prefix:
                o_lookup = owner_prefix.strip()
            elif owner_email:
                oe = owner_email.strip()
                o_lookup = oe.split("@", 1)[0] if "@" in oe else oe
            if o_lookup:
                res_o = await session.execute(select(User).where(User.email_prefix == o_lookup))
                o = res_o.scalars().first()
                if o:
                    project.owner_id = o.id
        # 其它字段直接赋值
        for field, value in update_data.items():
            if field == 'description':
                setattr(project, field, sanitize_html(value))
            else:
                setattr(project, field, value)
        
        project.updated_at = datetime.utcnow()
        await session.flush()
        await session.refresh(project)
        
        return project
    
    async def archive_project(
        self, 
        session: AsyncSession, 
        project_id: int, 
        current_user_id: int
    ) -> Optional[Project]:
        """
        归档项目
        
        Args:
            session: 数据库会话
            project_id: 项目ID
            current_user_id: 当前用户ID（用于权限验证）
            
        Returns:
            归档后的项目对象，如果不存在返回None
        """
        project = await self.get_project(session, project_id)
        if not project:
            return None
        
        # 权限验证：只有项目所有者可以归档项目
        if project.owner_id != current_user_id:
            raise ForbiddenException("只有项目所有者可以归档项目")
        
        # 归档项目
        project.archived = True
        project.status = "archived"
        project.updated_at = datetime.utcnow()
        
        await session.flush()
        await session.refresh(project)
        
        return project
    
    async def unarchive_project(
        self, 
        session: AsyncSession, 
        project_id: int, 
        current_user_id: int
    ) -> Optional[Project]:
        """
        取消归档项目
        
        Args:
            session: 数据库会话
            project_id: 项目ID
            current_user_id: 当前用户ID（用于权限验证）
            
        Returns:
            取消归档后的项目对象，如果不存在返回None
        """
        project = await self.get_project(session, project_id)
        if not project:
            return None
        
        # 权限验证：只有项目所有者可以取消归档项目
        if project.owner_id != current_user_id:
            raise ForbiddenException("只有项目所有者可以取消归档项目")
        
        # 取消归档项目
        project.archived = False
        project.status = "active"
        project.updated_at = datetime.utcnow()
        
        await session.flush()
        await session.refresh(project)
        
        return project
    
    async def soft_delete_project(
        self, 
        session: AsyncSession, 
        project_id: int, 
        current_user_id: int
    ) -> Optional[Project]:
        """
        软删除项目
        
        Args:
            session: 数据库会话
            project_id: 项目ID
            current_user_id: 当前用户ID（用于权限验证）
            
        Returns:
            软删除后的项目对象，如果不存在返回None
        """
        project = await self.get_project(session, project_id)
        if not project:
            return None
        
        # 权限验证：只有项目所有者可以删除项目
        if project.owner_id != current_user_id:
            raise ForbiddenException("只有项目所有者可以删除项目")
        
        # 软删除项目
        project.deleted_at = datetime.utcnow()
        project.updated_at = datetime.utcnow()
        
        await session.flush()
        await session.refresh(project)
        
        return project
    
    async def restore_project(
        self, 
        session: AsyncSession, 
        project_id: int, 
        current_user_id: int
    ) -> Optional[Project]:
        """
        恢复软删除的项目
        
        Args:
            session: 数据库会话
            project_id: 项目ID
            current_user_id: 当前用户ID（用于权限验证）
            
        Returns:
            恢复后的项目对象，如果不存在返回None
        """
        # 获取包括已删除的项目
        project = await self.get_project(session, project_id, include_deleted=True)
        if not project:
            return None
        
        # 检查是否已删除
        if project.deleted_at is None:
            return project  # 未删除，直接返回
        
        # 权限验证：只有项目所有者可以恢复项目
        if project.owner_id != current_user_id:
            raise ForbiddenException("只有项目所有者可以恢复项目")
        
        # 恢复项目
        project.deleted_at = None
        project.updated_at = datetime.utcnow()
        
        await session.flush()
        await session.refresh(project)
        
        return project
    
    async def get_project_statistics(
        self, 
        session: AsyncSession, 
        project_id: int
    ) -> dict:
        """
        获取项目统计信息
        
        Args:
            session: 数据库会话
            project_id: 项目ID
            
        Returns:
            统计信息字典
        """
        # 检查项目是否存在
        project = await self.get_project(session, project_id)
        if not project:
            raise NotFoundException("项目不存在")
        
        # 获取工作项统计
        stmt = select(
            func.count(WorkItem.id).label('total_count'),
            func.sum(func.case((WorkItem.status == 'todo', 1), else_=0)).label('todo_count'),
            func.sum(func.case((WorkItem.status == 'doing', 1), else_=0)).label('doing_count'),
            func.sum(func.case((WorkItem.status == 'done', 1), else_=0)).label('done_count')
        ).where(
            and_(
                WorkItem.project_id == project_id,
                WorkItem.deleted_at.is_(None)
            )
        )
        
        result = await session.execute(stmt)
        stats = result.one()
        
        return {
            "project_id": project_id,
            "total_work_items": stats.total_count or 0,
            "todo_count": stats.todo_count or 0,
            "doing_count": stats.doing_count or 0,
            "done_count": stats.done_count or 0
        }


# 创建全局实例
project_service = ProjectService()
