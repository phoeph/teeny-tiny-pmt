import pytest
import asyncio
from datetime import datetime, date
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import (
    User, Project, WorkItem, Comment, Attachment, Mention, 
    Notification, Sequence, Base
)
from app.database import engine, get_db


class TestModels:
    """测试数据模型"""
    
    @pytest.mark.asyncio
    async def test_user_creation(self):
        """测试用户创建"""
        async with AsyncSession(engine) as session:
            # 创建用户
            user = User(
                username="testuser",
                email_prefix="testuser",
                password_hash="hashed_password_123",
                is_active=True
            )
            session.add(user)
            await session.commit()
            
            # 验证用户创建
            result = await session.execute(select(User).where(User.username == "testuser"))
            found_user = result.scalar_one_or_none()
            
            assert found_user is not None
            assert found_user.username == "testuser"
            assert found_user.email_prefix == "testuser"
            assert found_user.is_active is True
            assert found_user.created_at is not None
            
            # 清理
            await session.delete(found_user)
            await session.commit()
    
    @pytest.mark.asyncio
    async def test_project_creation(self):
        """测试项目创建"""
        async with AsyncSession(engine) as session:
            # 先创建用户
            user = User(
                username="projectowner",
                email_prefix="projectowner", 
                password_hash="hashed_password_456"
            )
            session.add(user)
            await session.flush()
            
            # 创建项目
            project = Project(
                code="PRO-0001",
                name="测试项目",
                description="这是一个测试项目",
                owner_id=user.id,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31),
                status="active",
                archived=False
            )
            session.add(project)
            await session.commit()
            
            # 验证项目创建
            result = await session.execute(select(Project).where(Project.code == "PRO-0001"))
            found_project = result.scalar_one_or_none()
            
            assert found_project is not None
            assert found_project.code == "PRO-0001"
            assert found_project.name == "测试项目"
            assert found_project.owner_id == user.id
            assert found_project.status == "active"
            assert found_project.archived is False
            
            # 清理
            await session.delete(found_project)
            await session.delete(user)
            await session.commit()
    
    @pytest.mark.asyncio
    async def test_work_item_creation(self):
        """测试工作项创建（任务和子任务）"""
        async with AsyncSession(engine) as session:
            # 创建用户和项目
            user = User(
                username="workuser",
                email_prefix="workuser",
                password_hash="hashed_password_789"
            )
            session.add(user)
            await session.flush()
            
            project = Project(
                code="PRO-0002",
                name="工作项测试项目",
                owner_id=user.id
            )
            session.add(project)
            await session.flush()
            
            # 创建任务（JOB）
            job = WorkItem(
                code="JOB-0001",
                kind="JOB",
                project_id=project.id,
                title="主要任务",
                description="这是一个主要任务",
                assignee_id=user.id,
                status="todo",
                priority="high",
                creator_id=user.id
            )
            session.add(job)
            await session.flush()
            
            # 创建子任务（TASK）
            task = WorkItem(
                code="TASK-0001",
                kind="TASK",
                project_id=project.id,
                parent_id=job.id,
                title="子任务",
                description="这是一个子任务",
                assignee_id=user.id,
                status="todo",
                priority="medium",
                creator_id=user.id
            )
            session.add(task)
            await session.commit()
            
            # 验证任务创建
            result = await session.execute(select(WorkItem).where(WorkItem.code == "JOB-0001"))
            found_job = result.scalar_one_or_none()
            
            assert found_job is not None
            assert found_job.kind == "JOB"
            assert found_job.parent_id is None
            assert found_job.title == "主要任务"
            
            # 验证子任务创建
            result = await session.execute(select(WorkItem).where(WorkItem.code == "TASK-0001"))
            found_task = result.scalar_one_or_none()
            
            assert found_task is not None
            assert found_task.kind == "TASK"
            assert found_task.parent_id == job.id
            assert found_task.title == "子任务"
            
            # 清理
            await session.delete(task)
            await session.delete(job)
            await session.delete(project)
            await session.delete(user)
            await session.commit()
    
    @pytest.mark.asyncio
    async def test_work_item_constraints(self):
        """测试工作项约束条件"""
        async with AsyncSession(engine) as session:
            # 创建用户和项目
            user = User(
                username="constraintuser",
                email_prefix="constraintuser",
                password_hash="hashed_password_101"
            )
            session.add(user)
            await session.flush()
            
            project = Project(
                code="PRO-0003",
                name="约束测试项目",
                owner_id=user.id
            )
            session.add(project)
            await session.flush()
            
            # 测试1：JOB不能有parent_id
            job_with_parent = WorkItem(
                code="JOB-0002",
                kind="JOB",
                project_id=project.id,
                parent_id=999,  # 非法parent_id
                title="有父任务的任务",
                creator_id=user.id
            )
            session.add(job_with_parent)
            
            # 这应该失败，因为JOB不能有parent_id
            with pytest.raises(Exception):
                await session.commit()
            
            await session.rollback()
            
            # 测试2：TASK必须有parent_id
            task_without_parent = WorkItem(
                code="TASK-0002",
                kind="TASK",
                project_id=project.id,
                parent_id=None,  # TASK必须有parent_id
                title="没有父任务的子任务",
                creator_id=user.id
            )
            session.add(task_without_parent)
            
            # 这应该失败，因为TASK必须有parent_id
            with pytest.raises(Exception):
                await session.commit()
            
            # 清理
            await session.delete(user)
            await session.commit()
    
    @pytest.mark.asyncio
    async def test_comment_creation(self):
        """测试评论创建"""
        async with AsyncSession(engine) as session:
            # 创建用户和项目
            user = User(
                username="commentuser",
                email_prefix="commentuser",
                password_hash="hashed_password_102"
            )
            session.add(user)
            await session.flush()
            
            project = Project(
                code="PRO-0004",
                name="评论测试项目",
                owner_id=user.id
            )
            session.add(project)
            await session.flush()
            
            # 创建评论在项目
            comment = Comment(
                entity_type="project",
                entity_id=project.id,
                author_id=user.id,
                content="这是一个项目评论"
            )
            session.add(comment)
            await session.commit()
            
            # 验证评论创建
            result = await session.execute(select(Comment).where(Comment.content == "这是一个项目评论"))
            found_comment = result.scalar_one_or_none()
            
            assert found_comment is not None
            assert found_comment.entity_type == "project"
            assert found_comment.entity_id == project.id
            assert found_comment.author_id == user.id
            
            # 清理
            await session.delete(comment)
            await session.delete(project)
            await session.delete(user)
            await session.commit()
    
    @pytest.mark.asyncio
    async def test_sequence_creation(self):
        """测试序列创建"""
        async with AsyncSession(engine) as session:
            # 创建序列
            sequence = Sequence(
                prefix="PRO",
                current_value=0
            )
            session.add(sequence)
            await session.commit()
            
            # 验证序列创建
            result = await session.execute(select(Sequence).where(Sequence.prefix == "PRO"))
            found_sequence = result.scalar_one_or_none()
            
            assert found_sequence is not None
            assert found_sequence.prefix == "PRO"
            assert found_sequence.current_value == 0
            
            # 清理
            await session.delete(found_sequence)
            await session.commit()
    
    @pytest.mark.asyncio
    async def test_soft_delete_functionality(self):
        """测试软删除功能"""
        async with AsyncSession(engine) as session:
            # 创建用户和项目
            user = User(
                username="softdeleteuser",
                email_prefix="softdeleteuser",
                password_hash="hashed_password_103"
            )
            session.add(user)
            await session.flush()
            
            project = Project(
                code="PRO-0005",
                name="软删除测试项目",
                owner_id=user.id
            )
            session.add(project)
            await session.commit()
            
            # 软删除项目
            project.deleted_at = datetime.now()
            await session.commit()
            
            # 验证软删除 - 正常查询应该找不到
            result = await session.execute(
                select(Project).where(
                    Project.code == "PRO-0005",
                    Project.deleted_at.is_(None)
                )
            )
            found_project = result.scalar_one_or_none()
            assert found_project is None
            
            # 但包含软删除数据的查询应该能找到
            result = await session.execute(
                select(Project).where(Project.code == "PRO-0005")
            )
            found_project_with_deleted = result.scalar_one_or_none()
            assert found_project_with_deleted is not None
            assert found_project_with_deleted.deleted_at is not None
            
            # 清理
            await session.delete(project)
            await session.delete(user)
            await session.commit()
    
    @pytest.mark.asyncio
    async def test_database_tables_exist(self):
        """测试所有数据库表都存在"""
        async with AsyncSession(engine) as session:
            # 查询sqlite_master获取所有表
            result = await session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = [row[0] for row in result.fetchall()]
            
            # 验证核心表存在
            expected_tables = [
                'users', 'projects', 'work_items', 'comments', 
                'attachments', 'mentions', 'notifications', 'sequences',
                'alembic_version'  # Alembic版本表
            ]
            
            for table in expected_tables:
                assert table in tables, f"表 {table} 不存在"
            
            print(f"发现的数据库表: {tables}")


class TestModelRelationships:
    """测试模型关系"""
    
    @pytest.mark.asyncio
    async def test_user_project_relationship(self):
        """测试用户-项目关系"""
        async with AsyncSession(engine) as session:
            # 创建用户
            user = User(
                username="relationuser",
                email_prefix="relationuser",
                password_hash="hashed_password_104"
            )
            session.add(user)
            await session.flush()
            
            # 创建项目
            project1 = Project(
                code="PRO-0006",
                name="关系测试项目1",
                owner_id=user.id
            )
            project2 = Project(
                code="PRO-0007",
                name="关系测试项目2",
                owner_id=user.id
            )
            session.add(project1)
            session.add(project2)
            await session.commit()
            
            # 验证关系
            result = await session.execute(select(User).where(User.username == "relationuser"))
            found_user = result.scalar_one_or_none()
            
            assert found_user is not None
            assert len(found_user.owned_projects) == 2
            assert found_user.owned_projects[0].owner_id == user.id
            assert found_user.owned_projects[1].owner_id == user.id
            
            # 清理
            await session.delete(project1)
            await session.delete(project2)
            await session.delete(user)
            await session.commit()
    
    @pytest.mark.asyncio
    async def test_project_work_item_relationship(self):
        """测试项目-工作项关系"""
        async with AsyncSession(engine) as session:
            # 创建用户和项目
            user = User(
                username="workrelationuser",
                email_prefix="workrelationuser",
                password_hash="hashed_password_105"
            )
            session.add(user)
            await session.flush()
            
            project = Project(
                code="PRO-0008",
                name="工作项关系测试项目",
                owner_id=user.id
            )
            session.add(project)
            await session.flush()
            
            # 创建工作项
            work_item1 = WorkItem(
                code="JOB-0003",
                kind="JOB",
                project_id=project.id,
                title="工作项1",
                creator_id=user.id
            )
            work_item2 = WorkItem(
                code="JOB-0004",
                kind="JOB",
                project_id=project.id,
                title="工作项2",
                creator_id=user.id
            )
            session.add(work_item1)
            session.add(work_item2)
            await session.commit()
            
            # 验证关系
            result = await session.execute(select(Project).where(Project.code == "PRO-0008"))
            found_project = result.scalar_one_or_none()
            
            assert found_project is not None
            assert len(found_project.work_items) == 2
            assert found_project.work_items[0].project_id == project.id
            assert found_project.work_items[1].project_id == project.id
            
            # 清理
            await session.delete(work_item1)
            await session.delete(work_item2)
            await session.delete(project)
            await session.delete(user)
            await session.commit()
    
    @pytest.mark.asyncio
    async def test_work_item_parent_child_relationship(self):
        """测试工作项父子关系"""
        async with AsyncSession(engine) as session:
            # 创建用户和项目
            user = User(
                username="parentchilduser",
                email_prefix="parentchilduser",
                password_hash="hashed_password_106"
            )
            session.add(user)
            await session.flush()
            
            project = Project(
                code="PRO-0009",
                name="父子关系测试项目",
                owner_id=user.id
            )
            session.add(project)
            await session.flush()
            
            # 创建父工作项
            parent_work_item = WorkItem(
                code="JOB-0005",
                kind="JOB",
                project_id=project.id,
                title="父工作项",
                creator_id=user.id
            )
            session.add(parent_work_item)
            await session.flush()
            
            # 创建子工作项
            child_work_item = WorkItem(
                code="TASK-0003",
                kind="TASK",
                project_id=project.id,
                parent_id=parent_work_item.id,
                title="子工作项",
                creator_id=user.id
            )
            session.add(child_work_item)
            await session.commit()
            
            # 验证父子关系
            result = await session.execute(select(WorkItem).where(WorkItem.code == "JOB-0005"))
            found_parent = result.scalar_one_or_none()
            
            assert found_parent is not None
            assert len(found_parent.subtasks) == 1
            assert found_parent.subtasks[0].code == "TASK-0003"
            assert found_parent.subtasks[0].parent_id == parent_work_item.id
            
            # 验证子项的父关系
            result = await session.execute(select(WorkItem).where(WorkItem.code == "TASK-0003"))
            found_child = result.scalar_one_or_none()
            
            assert found_child is not None
            assert found_child.parent.code == "JOB-0005"
            
            # 清理
            await session.delete(child_work_item)
            await session.delete(parent_work_item)
            await session.delete(project)
            await session.delete(user)
            await session.commit()