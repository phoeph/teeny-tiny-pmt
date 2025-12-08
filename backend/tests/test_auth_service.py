"""
测试认证服务
"""
import pytest
import asyncio
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User
from app.services.auth_service import auth_service
from app.config import settings


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
async def test_password_hashing():
    """测试密码哈希"""
    password = "test_password_123"
    
    # 生成密码哈希
    hashed_password = auth_service.get_password_hash(password)
    assert hashed_password != password
    assert len(hashed_password) > 0
    
    # 验证正确密码
    assert auth_service.verify_password(password, hashed_password) is True
    
    # 验证错误密码
    assert auth_service.verify_password("wrong_password", hashed_password) is False


@pytest.mark.asyncio
async def test_create_and_verify_access_token():
    """测试创建和验证访问令牌"""
    # 创建令牌
    data = {"sub": "testuser", "user_id": 123}
    token = auth_service.create_access_token(data)
    
    assert token is not None
    assert len(token) > 0
    
    # 验证令牌
    decoded_data = auth_service.verify_token(token)
    assert decoded_data is not None
    assert decoded_data["username"] == "testuser"


@pytest.mark.asyncio
async def test_authenticate_user_with_username():
    """测试使用用户名认证用户"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 创建测试用户
            password_hash = auth_service.get_password_hash("test_password")
            user = User(
                username="testuser",
                email_prefix="testuser",
                password_hash=password_hash,
                is_active=True
            )
            session.add(user)
            await session.commit()
            
            # 使用用户名认证
            authenticated_user = await auth_service.authenticate_user(
                session, "testuser", "test_password"
            )
            
            assert authenticated_user is not None
            assert authenticated_user.username == "testuser"
            assert authenticated_user.email_prefix == "testuser"
            
            # 测试错误密码
            wrong_password_user = await auth_service.authenticate_user(
                session, "testuser", "wrong_password"
            )
            assert wrong_password_user is None
            
            # 测试不存在的用户
            nonexistent_user = await auth_service.authenticate_user(
                session, "nonexistent", "test_password"
            )
            assert nonexistent_user is None
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_authenticate_user_with_email_prefix():
    """测试使用邮箱前缀认证用户"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 创建测试用户
            password_hash = auth_service.get_password_hash("test_password")
            user = User(
                username="测试用户",
                email_prefix="testuser",
                password_hash=password_hash,
                is_active=True
            )
            session.add(user)
            await session.commit()
            
            # 使用邮箱前缀认证
            authenticated_user = await auth_service.authenticate_user(
                session, "testuser", "test_password"
            )
            
            assert authenticated_user is not None
            assert authenticated_user.username == "测试用户"
            assert authenticated_user.email_prefix == "testuser"
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_authenticate_inactive_user():
    """测试认证非激活用户"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 创建非激活用户
            password_hash = auth_service.get_password_hash("test_password")
            user = User(
                username="inactiveuser",
                email_prefix="inactiveuser",
                password_hash=password_hash,
                is_active=False  # 非激活
            )
            session.add(user)
            await session.commit()
            
            # 尝试认证非激活用户
            authenticated_user = await auth_service.authenticate_user(
                session, "inactiveuser", "test_password"
            )
            assert authenticated_user is None
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_get_current_user():
    """测试获取当前用户"""
    await create_tables()
    
    try:
        async with AsyncTestSession() as session:
            # 创建测试用户
            password_hash = auth_service.get_password_hash("test_password")
            user = User(
                username="currentuser",
                email_prefix="currentuser",
                password_hash=password_hash,
                is_active=True
            )
            session.add(user)
            await session.commit()
            
            # 创建令牌
            token = auth_service.create_access_token({"sub": "currentuser"})
            
            # 获取当前用户
            current_user = await auth_service.get_current_user(session, token)
            
            assert current_user is not None
            assert current_user.username == "currentuser"
            assert current_user.email_prefix == "currentuser"
            
            # 测试无效令牌
            invalid_token = "invalid_token"
            invalid_user = await auth_service.get_current_user(session, invalid_token)
            assert invalid_user is None
            
    finally:
        await drop_tables()


@pytest.mark.asyncio
async def test_token_expiration():
    """测试令牌过期"""
    # 创建过期令牌
    data = {"sub": "testuser"}
    expired_token = auth_service.create_access_token(
        data, expires_delta=timedelta(seconds=-1)  # 已过期
    )
    
    # 验证过期令牌应该失败
    decoded_data = auth_service.verify_token(expired_token)
    assert decoded_data is None


if __name__ == "__main__":
    # 运行所有测试
    asyncio.run(test_password_hashing())
    asyncio.run(test_create_and_verify_access_token())
    asyncio.run(test_authenticate_user_with_username())
    asyncio.run(test_authenticate_user_with_email_prefix())
    asyncio.run(test_authenticate_inactive_user())
    asyncio.run(test_get_current_user())
    asyncio.run(test_token_expiration())
    print("所有认证服务测试通过！")