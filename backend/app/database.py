from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os
import asyncio
import logging

from .config import DATABASE_URL

logger = logging.getLogger(__name__)

# 判断是否为生产环境
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=not IS_PRODUCTION,  # 生产环境禁用 SQL 日志
    future=True,
    pool_pre_ping=True,  # 连接池健康检查
    pool_recycle=3600,  # 1小时回收连接，防止 MySQL 超时
    pool_size=10,  # 连接池大小
    max_overflow=20  # 最大溢出连接数
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def test_database_connection(max_retries: int = 5, retry_interval: int = 5) -> bool:
    """
    测试数据库连接
    
    Args:
        max_retries: 最大重试次数
        retry_interval: 重试间隔（秒）
    
    Returns:
        bool: 连接成功返回 True，否则抛出异常
    
    Raises:
        RuntimeError: 多次重试后仍无法连接数据库
    """
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                logger.info(f"⏳ Retrying in {retry_interval} seconds...")
                await asyncio.sleep(retry_interval)
            else:
                error_msg = f"Failed to connect to database after {max_retries} retries"
                logger.error(f"❌ {error_msg}")
                raise RuntimeError(error_msg)
    
    return False
