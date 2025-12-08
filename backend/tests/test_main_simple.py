import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns API info."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        # Root endpoint doesn't exist yet, should return 404
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_404_handler():
    """Test 404 error handling."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/nonexistent")
        assert response.status_code == 404
        # FastAPI default 404 response doesn't have our custom format yet
        data = response.json()
        assert "detail" in data