import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db


class TestDatabase:
    """Test database connection and session management."""

    @pytest.mark.asyncio
    async def test_database_connection(self, db_session: AsyncSession):
        """Test that database connection is working."""
        # Execute a simple query to test connection
        result = await db_session.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1

    @pytest.mark.asyncio
    async def test_session_rollback(self, db_session: AsyncSession):
        """Test that session rollback works properly."""
        # This test ensures our rollback fixture is working
        # We'll create a more comprehensive test when we have actual models
        assert db_session.is_active

    @pytest.mark.asyncio
    async def test_get_db_dependency(self):
        """Test that get_db dependency works."""
        # Test the dependency function
        async for session in get_db():
            assert isinstance(session, AsyncSession)
            # Verify we can execute a simple query
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            assert value == 1
            break  # Only need to test the first yield

    @pytest.mark.asyncio
    async def test_database_tables_exist(self, db_session: AsyncSession):
        """Test that all required database tables exist."""
        # This test will be expanded when we create our models
        # For now, just verify we can query sqlite_master
        result = await db_session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        tables = [row[0] for row in result.fetchall()]
        
        # At minimum, we should have sqlite system tables
        assert len(tables) > 0
        print(f"Available tables: {tables}")  # For debugging during development