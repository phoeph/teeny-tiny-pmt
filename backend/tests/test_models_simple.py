import pytest
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine


class TestModelsSimple:
    """简化版数据模型测试"""
    
    @pytest.mark.asyncio
    async def test_database_tables_exist(self):
        """测试所有数据库表都存在"""
        async with AsyncSession(engine) as session:
            # 查询sqlite_master获取所有表
            result = await session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = [row[0] for row in result.fetchall()]
            
            print(f"发现的数据库表: {tables}")
            
            # 验证核心表存在
            expected_tables = [
                'users', 'projects', 'work_items', 'comments', 
                'attachments', 'mentions', 'notifications', 'sequences'
            ]
            
            for table in expected_tables:
                assert table in tables, f"表 {table} 不存在"
    
    @pytest.mark.asyncio
    async def test_table_constraints_exist(self):
        """测试表约束存在"""
        async with AsyncSession(engine) as session:
            # 查询表信息
            result = await session.execute(
                text("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
            )
            users_sql = result.scalar_one_or_none()
            
            assert users_sql is not None
            assert "username" in users_sql
            assert "email_prefix" in users_sql
            assert "password_hash" in users_sql
            
            # 查询projects表
            result = await session.execute(
                text("SELECT sql FROM sqlite_master WHERE type='table' AND name='projects'")
            )
            projects_sql = result.scalar_one_or_none()
            
            assert projects_sql is not None
            assert "code" in projects_sql
            assert "owner_id" in projects_sql
            assert "deleted_at" in projects_sql
            
            # 查询work_items表
            result = await session.execute(
                text("SELECT sql FROM sqlite_master WHERE type='table' AND name='work_items'")
            )
            work_items_sql = result.scalar_one_or_none()
            
            assert work_items_sql is not None
            assert "code" in work_items_sql
            assert "kind" in work_items_sql
            assert "parent_id" in work_items_sql
            assert "deleted_at" in work_items_sql
    
    @pytest.mark.asyncio
    async def test_indexes_exist(self):
        """测试索引存在"""
        async with AsyncSession(engine) as session:
            # 查询索引
            result = await session.execute(
                text("SELECT name FROM sqlite_master WHERE type='index'")
            )
            indexes = [row[0] for row in result.fetchall()]
            
            print(f"发现的索引: {indexes}")
            
            # 验证关键索引存在
            expected_indexes = [
                'ix_users_username',
                'ix_users_email_prefix',
                'ix_projects_code',
                'ix_work_items_code'
            ]
            
            for index in expected_indexes:
                # SQLite可能使用不同的索引命名，我们检查是否包含关键字段
                found = any(expected_field in idx for idx in indexes for expected_field in [index])
                assert found or index in indexes, f"索引 {index} 不存在"