"""
基础模型测试 - 验证核心实体的CRUD操作和软删除功能
"""
import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Project, WorkItem, Sequence
from app.database import get_db

# 使用内存数据库进行测试
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
AsyncTestSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def db_session():
    """创建测试数据库会话"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncTestSession() as session:
        yield session
        await session.rollback()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class TestModelsBasic:
    """基础模型测试类"""

    @pytest.mark.asyncio
    async def test_user_crud(self, db_session):
        """测试用户CRUD操作"""
        # 创建用户
        user = User(
            username="testuser_basic",
            email_prefix="testuser_basic",
            password_hash="hashed_password_123"
        )
        db_session.add(user)
        await db_session.commit()
        
        # 验证用户创建成功
        assert user.id is not None
        assert user.username == "testuser_basic"
        assert user.is_active is True
        
        # 查询用户
        found_user = await db_session.get(User, user.id)
        assert found_user is not None
        assert found_user.username == "testuser_basic"
        
        # 更新用户
        found_user.username = "updated_user"
        await db_session.commit()
        
        updated_user = await db_session.get(User, user.id)
        assert updated_user.username == "updated_user"
        
        # 软删除用户
        found_user.deleted_at = date.today()
        await db_session.commit()
        
        # 验证软删除
        deleted_user = await db_session.get(User, user.id)
        assert deleted_user.deleted_at is not None

    @pytest.mark.asyncio
    async def test_project_crud(self, db_session):
        """测试项目CRUD操作 - 简化版，避免关系映射问题"""
        # 创建项目
        project = Project(
            code="PRO-BASIC-001",
            name="基础测试项目",
            description="这是一个基础测试项目",
            owner_id=1,  # 使用固定ID，避免关系加载
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            status="active",
            archived=False
        )
        db_session.add(project)
        await db_session.commit()
        
        # 验证项目创建成功
        assert project.id is not None
        assert project.code == "PRO-BASIC-001"
        assert project.name == "基础测试项目"
        
        # 查询项目
        found_project = await db_session.get(Project, project.id)
        assert found_project is not None
        assert found_project.code == "PRO-BASIC-001"
        
        # 更新项目
        found_project.name = "更新后的项目"
        await db_session.commit()
        
        updated_project = await db_session.get(Project, project.id)
        assert updated_project.name == "更新后的项目"
        
        # 软删除项目
        found_project.deleted_at = date.today()
        await db_session.commit()
        
        # 验证软删除
        deleted_project = await db_session.get(Project, project.id)
        assert deleted_project.deleted_at is not None

    @pytest.mark.asyncio
    async def test_work_item_crud(self, db_session):
        """测试工作项CRUD操作 - 简化版"""
        # 创建工作项
        work_item = WorkItem(
            code="JOB-BASIC-001",
            kind="JOB",
            project_id=1,  # 使用固定ID
            title="基础任务",
            description="这是一个基础任务",
            assignee_id=1,  # 使用固定ID
            status="todo",
            priority="high",
            creator_id=1  # 使用固定ID
        )
        db_session.add(work_item)
        await db_session.commit()
        
        # 验证工作项创建成功
        assert work_item.id is not None
        assert work_item.code == "JOB-BASIC-001"
        assert work_item.kind == "JOB"
        assert work_item.title == "基础任务"
        
        # 查询工作项
        found_work_item = await db_session.get(WorkItem, work_item.id)
        assert found_work_item is not None
        assert found_work_item.code == "JOB-BASIC-001"
        
        # 更新工作项
        found_work_item.title = "更新后的任务"
        found_work_item.status = "in_progress"
        await db_session.commit()
        
        updated_work_item = await db_session.get(WorkItem, work_item.id)
        assert updated_work_item.title == "更新后的任务"
        assert updated_work_item.status == "in_progress"
        
        # 软删除工作项
        found_work_item.deleted_at = date.today()
        await db_session.commit()
        
        # 验证软删除
        deleted_work_item = await db_session.get(WorkItem, work_item.id)
        assert deleted_work_item.deleted_at is not None

    @pytest.mark.asyncio
    async def test_sequence_crud(self, db_session):
        """测试序列CRUD操作"""
        # 创建序列
        sequence = Sequence(
            prefix="PRO",
            current_value=1000,
            year=2024
        )
        db_session.add(sequence)
        await db_session.commit()
        
        # 验证序列创建成功
        assert sequence.id is not None
        assert sequence.prefix == "PRO"
        assert sequence.current_value == 1000
        assert sequence.year == 2024
        
        # 查询序列
        found_sequence = await db_session.get(Sequence, sequence.id)
        assert found_sequence is not None
        assert found_sequence.prefix == "PRO"
        
        # 更新序列
        found_sequence.current_value = 1001
        await db_session.commit()
        
        updated_sequence = await db_session.get(Sequence, sequence.id)
        assert updated_sequence.current_value == 1001
        
        # 软删除序列
        found_sequence.deleted_at = date.today()
        await db_session.commit()
        
        # 验证软删除
        deleted_sequence = await db_session.get(Sequence, sequence.id)
        assert deleted_sequence.deleted_at is not None

    @pytest.mark.asyncio
    async def test_work_item_kind_constraint(self, db_session):
        """测试工作项类型约束"""
        # 创建JOB类型的工作项
        job_item = WorkItem(
            code="JOB-TEST-001",
            kind="JOB",
            project_id=1,
            title="测试任务",
            creator_id=1
        )
        db_session.add(job_item)
        await db_session.commit()
        
        # 创建TASK类型的工作项
        task_item = WorkItem(
            code="TASK-TEST-001",
            kind="TASK",
            project_id=1,
            title="测试子任务",
            parent_id=job_item.id,  # TASK必须有父级
            creator_id=1
        )
        db_session.add(task_item)
        await db_session.commit()
        
        # 验证创建成功
        assert job_item.id is not None
        assert task_item.id is not None
        assert task_item.parent_id == job_item.id

    @pytest.mark.asyncio
    async def test_soft_delete_functionality(self, db_session):
        """测试软删除功能"""
        # 创建用户
        user = User(
            username="delete_test",
            email_prefix="delete_test",
            password_hash="hashed_password"
        )
        db_session.add(user)
        await db_session.commit()
        
        # 软删除用户
        user.deleted_at = date.today()
        await db_session.commit()
        
        # 验证用户仍然存在（软删除）
        deleted_user = await db_session.get(User, user.id)
        assert deleted_user is not None
        assert deleted_user.deleted_at is not None
        
        # 创建项目
        project = Project(
            code="PRO-DELETE-001",
            name="删除测试项目",
            owner_id=user.id,
            deleted_at=date.today()  # 直接创建为已删除
        )
        db_session.add(project)
        await db_session.commit()
        
        # 验证项目存在但被软删除
        deleted_project = await db_session.get(Project, project.id)
        assert deleted_project is not None
        assert deleted_project.deleted_at is not None