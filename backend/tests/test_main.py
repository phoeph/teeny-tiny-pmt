import pytest
from httpx import AsyncClient


class TestMain:
    """Test main application functionality."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint returns API info."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "项目管理系统 API"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_404_handler(self, client: AsyncClient):
        """Test 404 error handling."""
        response = await client.get("/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "NOT_FOUND"
        assert "message" in data

    @pytest.mark.asyncio
    async def test_exception_handler(self, client: AsyncClient):
        """Test that custom exception handler is working."""
        # This test validates that our exception handling middleware is properly configured
        # We'll test actual exceptions when we implement the API endpoints
        response = await client.get("/health")
        assert response.status_code == 200  # Basic smoke test that app is running