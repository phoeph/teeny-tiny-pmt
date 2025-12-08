"""
同步基础模型测试 - 验证核心实体基本功能
"""
import pytest
import asyncio
import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Project, WorkItem, Sequence

# 使用内存数据库进行测试
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
AsyncTestSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def generate_unique_code(prefix):
    """生成唯一的代码"""
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


async def create_tables():
    """创建所有表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """删除所有表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_user_crud():
    """测试用户CRUD操作"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 创建用户
            user = User(
                username=f"testuser_{uuid.uuid4().hex[:8]}",
                email_prefix=f"testuser_{uuid.uuid4().hex[:8]}", 
                password_hash="hashed_password_123"
            )
            session.add(user)
            await session.commit()
            
            # 验证用户创建成功
            assert user.id is not None
            assert "testuser_" in user.username
            assert user.is_active is True
            
            # 查询用户
            found_user = await session.get(User, user.id)
            assert found_user is not None
            assert found_user.username == user.username
            
            # 更新用户
            found_user.username = f"updated_user_{uuid.uuid4().hex[:8]}"
            await session.commit()
            
            updated_user = await session.get(User, user.id)
            assert "updated_user_" in updated_user.username
            
            # 软删除用户
            found_user.deleted_at = date.today()
            await session.commit()
            
            # 验证软删除
            deleted_user = await session.get(User, user.id)
            assert deleted_user.deleted_at is not None
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_project_crud():
    """测试项目CRUD操作"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 首先创建用户（项目需要owner_id）
            user = User(
                username=f"project_owner_{uuid.uuid4().hex[:8]}",
                email_prefix=f"project_owner_{uuid.uuid4().hex[:8]}", 
                password_hash="hashed_password_456"
            )
            session.add(user)
            await session.commit()
            
            # 创建项目
            project_code = generate_unique_code("PRO")
            project = Project(
                code=project_code,
                name="基础测试项目",
                description="这是一个基础测试项目",
                owner_id=user.id,  # 使用真实的用户ID
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31),
                status="active",
                archived=False
            )
            session.add(project)
            await session.commit()
            
            # 验证项目创建成功
            assert project.id is not None
            assert project.code == project_code
            assert project.name == "基础测试项目"
            
            # 查询项目
            found_project = await session.get(Project, project.id)
            assert found_project is not None
            assert found_project.code == project_code
            
            # 更新项目
            found_project.name = "更新后的项目"
            await session.commit()
            
            updated_project = await session.get(Project, project.id)
            assert updated_project.name == "更新后的项目"
            
            # 软删除项目
            found_project.deleted_at = date.today()
            await session.commit()
            
            # 验证软删除
            deleted_project = await session.get(Project, project.id)
            assert deleted_project.deleted_at is not None
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_work_item_crud():
    """测试工作项CRUD操作"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 首先创建用户和项目
            user = User(
                username=f"work_user_{uuid.uuid4().hex[:8]}",
                email_prefix=f"work_user_{uuid.uuid4().hex[:8]}", 
                password_hash="hashed_password_789"
            )
            session.add(user)
            await session.commit()
            
            project = Project(
                code=generate_unique_code("PRO"),
                name="工作项测试项目",
                owner_id=user.id
            )
            session.add(project)
            await session.commit()
            
            # 创建工作项
            work_item_code = generate_unique_code("JOB")
            work_item = WorkItem(
                code=work_item_code,
                kind="JOB",
                project_id=project.id,  # 使用真实的项目ID
                title="基础任务",
                description="这是一个基础任务",
                assignee_id=user.id,  # 使用真实的用户ID
                status="todo",
                priority="high",
                creator_id=user.id  # 使用真实的用户ID
            )
            session.add(work_item)
            await session.commit()
            
            # 验证工作项创建成功
            assert work_item.id is not None
            assert work_item.code == work_item_code
            assert work_item.kind == "JOB"
            assert work_item.title == "基础任务"
            
            # 查询工作项
            found_work_item = await session.get(WorkItem, work_item.id)
            assert found_work_item is not None
            assert found_work_item.code == work_item_code
            
            # 更新工作项
            found_work_item.title = "更新后的任务"
            found_work_item.status = "doing"
            await session.commit()
            
            updated_work_item = await session.get(WorkItem, work_item.id)
            assert updated_work_item.title == "更新后的任务"
            assert updated_work_item.status == "doing"
            
            # 软删除工作项
            found_work_item.deleted_at = date.today()
            await session.commit()
            
            # 验证软删除
            deleted_work_item = await session.get(WorkItem, work_item.id)
            assert deleted_work_item.deleted_at is not None
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_sequence_crud():
    """测试序列CRUD操作"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 创建序列 - 使用有效的前缀
            sequence = Sequence(
                prefix="PRO",  # 使用有效的前缀
                current_value=1000
            )
            session.add(sequence)
            await session.commit()
            
            # 验证序列创建成功
            assert sequence.prefix == "PRO"
            assert sequence.current_value == 1000
            
            # 查询序列
            found_sequence = await session.get(Sequence, sequence.prefix)
            assert found_sequence is not None
            assert found_sequence.prefix == "PRO"
            
            # 更新序列
            found_sequence.current_value = 1001
            await session.commit()
            
            updated_sequence = await session.get(Sequence, sequence.prefix)
            assert updated_sequence.current_value == 1001
            
            # 软删除序列（通过设置deleted_at）
            found_sequence.deleted_at = date.today()
            await session.commit()
            
            # 验证软删除
            deleted_sequence = await session.get(Sequence, sequence.prefix)
            assert deleted_sequence.deleted_at is not None
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_work_item_kind_constraint():
    """测试工作项类型约束"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 首先创建用户和项目
            user = User(
                username=f"constraint_user_{uuid.uuid4().hex[:8]}",
                email_prefix=f"constraint_user_{uuid.uuid4().hex[:8]}", 
                password_hash="hashed_password_123"
            )
            session.add(user)
            await session.commit()
            
            project = Project(
                code=generate_unique_code("PRO"),
                name="约束测试项目",
                owner_id=user.id
            )
            session.add(project)
            await session.commit()
            
            # 创建JOB类型的工作项
            job_item_code = generate_unique_code("JOB")
            job_item = WorkItem(
                code=job_item_code,
                kind="JOB",
                project_id=project.id,
                title="测试任务",
                creator_id=user.id
            )
            session.add(job_item)
            await session.commit()
            
            # 创建TASK类型的工作项
            task_item_code = generate_unique_code("TASK")
            task_item = WorkItem(
                code=task_item_code,
                kind="TASK",
                project_id=project.id,
                title="测试子任务",
                parent_id=job_item.id,  # TASK必须有父级
                creator_id=user.id
            )
            session.add(task_item)
            await session.commit()
            
            # 验证创建成功
            assert job_item.id is not None
            assert task_item.id is not None
            assert task_item.parent_id == job_item.id
            
    finally:
        await drop_tables()


if __name__ == "__main__":
    # 运行所有测试
    asyncio.run(test_user_crud())
    asyncio.run(test_project_crud())
    asyncio.run(test_work_item_crud())
    asyncio.run(test_sequence_crud())
    asyncio.run(test_work_item_kind_constraint())
    print("所有测试通过！")