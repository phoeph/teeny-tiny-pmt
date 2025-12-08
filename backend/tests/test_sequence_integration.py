"""
序列服务集成测试 - 验证与数据模型的集成
"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Project, WorkItem
from app.services.sequence_service import sequence_service


# 使用内存数据库进行测试
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
AsyncTestSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_tables():
    """创建所有表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """删除所有表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_project_with_auto_code():
    """测试使用序列服务创建项目"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 创建用户
            user = User(
                username="test_user",
                email_prefix="test_user", 
                password_hash="hashed_password"
            )
            session.add(user)
            await session.flush()
            
            # 使用序列服务生成项目编号
            project_code = await sequence_service.generate_code(session, "PRO")
            
            # 创建项目
            project = Project(
                code=project_code,
                name="测试项目",
                owner_id=user.id,
                status="active",
                archived=False
            )
            session.add(project)
            await session.commit()
            
            # 验证项目创建成功
            assert project.id is not None
            assert project.code == "PRO-1001"
            assert project.name == "测试项目"
            
            # 验证序列值已更新
            from app.models import Sequence
            sequence = await session.get(Sequence, "PRO")
            assert sequence.current_value == 1001
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_create_work_item_with_auto_code():
    """测试使用序列服务创建工作项"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 创建用户
            user = User(
                username="work_user",
                email_prefix="work_user", 
                password_hash="hashed_password"
            )
            session.add(user)
            await session.flush()
            
            # 创建项目
            project_code = await sequence_service.generate_code(session, "PRO")
            project = Project(
                code=project_code,
                name="工作项测试项目",
                owner_id=user.id,
                status="active",
                archived=False
            )
            session.add(project)
            await session.flush()
            
            # 使用序列服务生成工作项编号
            job_code = await sequence_service.generate_code(session, "JOB")
            
            # 创建工作项
            work_item = WorkItem(
                code=job_code,
                kind="JOB",
                project_id=project.id,
                title="测试任务",
                creator_id=user.id,
                status="todo",
                priority="high"
            )
            session.add(work_item)
            await session.commit()
            
            # 验证工作项创建成功
            assert work_item.id is not None
            assert work_item.code == "JOB-1001"
            assert work_item.kind == "JOB"
            assert work_item.title == "测试任务"
            
            # 验证序列值已更新
            from app.models import Sequence
            job_sequence = await session.get(Sequence, "JOB")
            assert job_sequence.current_value == 1001
            
            project_sequence = await session.get(Sequence, "PRO")
            assert project_sequence.current_value == 1001
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_create_subtask_with_auto_code():
    """测试使用序列服务创建子任务"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 创建用户
            user = User(
                username="subtask_user",
                email_prefix="subtask_user", 
                password_hash="hashed_password"
            )
            session.add(user)
            await session.flush()
            
            # 创建项目
            project_code = await sequence_service.generate_code(session, "PRO")
            project = Project(
                code=project_code,
                name="子任务测试项目",
                owner_id=user.id,
                status="active",
                archived=False
            )
            session.add(project)
            await session.flush()
            
            # 创建父任务
            job_code = await sequence_service.generate_code(session, "JOB")
            parent_task = WorkItem(
                code=job_code,
                kind="JOB",
                project_id=project.id,
                title="父任务",
                creator_id=user.id,
                status="todo",
                priority="medium"
            )
            session.add(parent_task)
            await session.flush()
            
            # 使用序列服务生成子任务编号
            task_code = await sequence_service.generate_code(session, "TASK")
            
            # 创建子任务
            subtask = WorkItem(
                code=task_code,
                kind="TASK",
                project_id=project.id,
                parent_id=parent_task.id,
                title="子任务",
                creator_id=user.id,
                status="todo",
                priority="low"
            )
            session.add(subtask)
            await session.commit()
            
            # 验证子任务创建成功
            assert subtask.id is not None
            assert subtask.code == "TASK-1001"
            assert subtask.kind == "TASK"
            assert subtask.parent_id == parent_task.id
            assert subtask.title == "子任务"
            
            # 验证序列值已更新
            from app.models import Sequence
            task_sequence = await session.get(Sequence, "TASK")
            assert task_sequence.current_value == 1001
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_multiple_entities_integration():
    """测试多个实体的集成创建"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 创建用户
            user = User(
                username="multi_user",
                email_prefix="multi_user", 
                password_hash="hashed_password"
            )
            session.add(user)
            await session.flush()
            
            # 创建多个项目
            project_codes = []
            for i in range(3):
                project_code = await sequence_service.generate_code(session, "PRO")
                project_codes.append(project_code)
                
                project = Project(
                    code=project_code,
                    name=f"项目{i+1}",
                    owner_id=user.id,
                    status="active",
                    archived=False
                )
                session.add(project)
            
            await session.flush()
            
            # 验证项目编号
            assert project_codes == ["PRO-1001", "PRO-1002", "PRO-1003"]
            
            # 创建多个工作项
            job_codes = []
            for i in range(3):
                job_code = await sequence_service.generate_code(session, "JOB")
                job_codes.append(job_code)
                
                work_item = WorkItem(
                    code=job_code,
                    kind="JOB",
                    project_id=1,  # 使用第一个项目
                    title=f"任务{i+1}",
                    creator_id=user.id,
                    status="todo",
                    priority="medium"
                )
                session.add(work_item)
            
            await session.commit()
            
            # 验证工作项编号
            assert job_codes == ["JOB-1001", "JOB-1002", "JOB-1003"]
            
            # 验证所有序列值
            from app.models import Sequence
            pro_sequence = await session.get(Sequence, "PRO")
            assert pro_sequence.current_value == 1003
            
            job_sequence = await session.get(Sequence, "JOB")
            assert job_sequence.current_value == 1003
            
    finally:
        await drop_tables()


if __name__ == "__main__":
    # 运行所有测试
    asyncio.run(test_create_project_with_auto_code())
    asyncio.run(test_create_work_item_with_auto_code())
    asyncio.run(test_create_subtask_with_auto_code())
    asyncio.run(test_multiple_entities_integration())
    print("所有序列集成测试通过！")