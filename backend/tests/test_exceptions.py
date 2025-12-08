import pytest
from httpx import AsyncClient
from app.exceptions import (
    AppException, BadRequestException, UnauthorizedException,
    NotFoundException, ConflictException, ValidationException
)


class TestExceptions:
    """Test custom exception classes."""

    def test_app_exception_base(self):
        """Test base AppException class."""
        exc = AppException(
            status_code=400,
            code="TEST_ERROR",
            message="Test error message",
            details={"field": "value"}
        )
        assert exc.status_code == 400
        assert exc.detail["code"] == "TEST_ERROR"
        assert exc.detail["message"] == "Test error message"
        assert exc.detail["details"] == {"field": "value"}

    def test_bad_request_exception(self):
        """Test BadRequestException."""
        exc = BadRequestException("Bad request test")
        assert exc.status_code == 400
        assert exc.detail["code"] == "BAD_REQUEST"
        assert exc.detail["message"] == "Bad request test"

    def test_unauthorized_exception(self):
        """Test UnauthorizedException."""
        exc = UnauthorizedException("Unauthorized test")
        assert exc.status_code == 401
        assert exc.detail["code"] == "UNAUTHORIZED"
        assert exc.detail["message"] == "Unauthorized test"

    def test_not_found_exception(self):
        """Test NotFoundException."""
        exc = NotFoundException("Not found test")
        assert exc.status_code == 404
        assert exc.detail["code"] == "NOT_FOUND"
        assert exc.detail["message"] == "Not found test"

    def test_conflict_exception(self):
        """Test ConflictException."""
        exc = ConflictException("Conflict test")
        assert exc.status_code == 409
        assert exc.detail["code"] == "CONFLICT"
        assert exc.detail["message"] == "Conflict test"

    def test_validation_exception(self):
        """Test ValidationException."""
        exc = ValidationException("Validation test", details={"field": "invalid"})
        assert exc.status_code == 422
        assert exc.detail["code"] == "VALIDATION_ERROR"
        assert exc.detail["message"] == "Validation test"
        assert exc.detail["details"] == {"field": "invalid"}

    def test_exception_with_details(self):
        """Test exception with additional details."""
        exc = BadRequestException(
            "Error with details",
            details={"field": "username", "reason": "already_exists"}
        )
        assert exc.detail["details"] == {"field": "username", "reason": "already_exists"}


class TestExceptionHandling:
    """Test exception handling in the application."""

    @pytest.mark.asyncio
    async def test_app_exception_handler(self, client: AsyncClient):
        """Test that AppException is properly handled."""
        # We'll test this more thoroughly when we implement endpoints
        # For now, just verify the app can handle the basic request
        response = await client.get("/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_general_exception_handler(self, client: AsyncClient):
        """Test that general exceptions are handled."""
        # Test a non-existent endpoint to verify 404 handling
        response = await client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "NOT_FOUND"
        assert "message" in data