"""
测试全局编号服务
"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Sequence
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
async def test_generate_project_code():
    """测试生成项目编号"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 生成第一个项目编号
            code1 = await sequence_service.generate_code(session, "PRO")
            assert code1 == "PRO-0001"
            
            # 生成第二个项目编号
            code2 = await sequence_service.generate_code(session, "PRO")
            assert code2 == "PRO-0002"
            
            # 验证序列记录
            sequence = await session.get(Sequence, "PRO")
            assert sequence.current_value == 2
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_generate_job_code():
    """测试生成任务编号"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 生成第一个任务编号
            code1 = await sequence_service.generate_code(session, "JOB")
            assert code1 == "JOB-0001"
            
            # 生成第二个任务编号
            code2 = await sequence_service.generate_code(session, "JOB")
            assert code2 == "JOB-0002"
            
            # 验证序列记录
            sequence = await session.get(Sequence, "JOB")
            assert sequence.current_value == 2
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_generate_task_code():
    """测试生成子任务编号"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 生成第一个子任务编号
            code1 = await sequence_service.generate_code(session, "TASK")
            assert code1 == "TASK-0001"
            
            # 生成第二个子任务编号
            code2 = await sequence_service.generate_code(session, "TASK")
            assert code2 == "TASK-0002"
            
            # 验证序列记录
            sequence = await session.get(Sequence, "TASK")
            assert sequence.current_value == 2
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_invalid_prefix():
    """测试无效前缀"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 尝试使用无效前缀
            with pytest.raises(ValueError, match="无效的前缀"):
                await sequence_service.generate_code(session, "INVALID")
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_get_next_value():
    """测试获取下一个序列值"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 先生成一个编号
            code1 = await sequence_service.generate_code(session, "PRO")
            assert code1 == "PRO-0001"
            
            # 获取下一个值（不增加）
            next_value = await sequence_service.get_next_value(session, "PRO")
            assert next_value == 2
            
            # 验证序列值没有变化
            sequence = await session.get(Sequence, "PRO")
            assert sequence.current_value == 1
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_reset_sequence():
    """测试重置序列"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 生成几个编号
            await sequence_service.generate_code(session, "PRO")
            await sequence_service.generate_code(session, "PRO")
            await sequence_service.generate_code(session, "PRO")
            
            # 验证当前值
            sequence = await session.get(Sequence, "PRO")
            assert sequence.current_value == 3
            
            # 重置序列
            await sequence_service.reset_sequence(session, "PRO", 2000)
            
            # 验证重置后的值
            sequence = await session.get(Sequence, "PRO")
            assert sequence.current_value == 2000
            
            # 生成新编号
            new_code = await sequence_service.generate_code(session, "PRO")
            assert new_code == "PRO-2001"
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_concurrent_generation():
    """测试并发编号生成"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 并发生成多个编号
            tasks = []
            for i in range(10):
                task = sequence_service.generate_code(session, "PRO")
                tasks.append(task)
            
            # 等待所有任务完成
            codes = await asyncio.gather(*tasks)
            
            # 验证所有编号都是唯一的
            assert len(set(codes)) == 10
            assert "PRO-0001" in codes
            assert "PRO-0010" in codes
            
            # 验证序列值
            sequence = await session.get(Sequence, "PRO")
            assert sequence.current_value == 10
            
    finally:
        await drop_tables()


if __name__ == "__main__":
    # 运行所有测试
    asyncio.run(test_generate_project_code())
    asyncio.run(test_generate_job_code())
    asyncio.run(test_generate_task_code())
    asyncio.run(test_invalid_prefix())
    asyncio.run(test_get_next_value())
    asyncio.run(test_reset_sequence())
    asyncio.run(test_concurrent_generation())
    print("所有序列服务测试通过！")
