import pytest
from app.exceptions import (
    AppException, BadRequestException, UnauthorizedException,
    NotFoundException, ConflictException, ValidationException
)


def test_app_exception_base():
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


def test_bad_request_exception():
    """Test BadRequestException."""
    exc = BadRequestException("Bad request test")
    assert exc.status_code == 400
    assert exc.detail["code"] == "BAD_REQUEST"
    assert exc.detail["message"] == "Bad request test"


def test_unauthorized_exception():
    """Test UnauthorizedException."""
    exc = UnauthorizedException("Unauthorized test")
    assert exc.status_code == 401
    assert exc.detail["code"] == "UNAUTHORIZED"
    assert exc.detail["message"] == "Unauthorized test"


def test_not_found_exception():
    """Test NotFoundException."""
    exc = NotFoundException("Not found test")
    assert exc.status_code == 404
    assert exc.detail["code"] == "NOT_FOUND"
    assert exc.detail["message"] == "Not found test"


def test_conflict_exception():
    """Test ConflictException."""
    exc = ConflictException("Conflict test")
    assert exc.status_code == 409
    assert exc.detail["code"] == "CONFLICT"
    assert exc.detail["message"] == "Conflict test"


def test_validation_exception():
    """Test ValidationException."""
    exc = ValidationException("Validation test", details={"field": "invalid"})
    assert exc.status_code == 422
    assert exc.detail["code"] == "VALIDATION_ERROR"
    assert exc.detail["message"] == "Validation test"
    assert exc.detail["details"] == {"field": "invalid"}


def test_exception_with_details():
    """Test exception with additional details."""
    exc = BadRequestException(
        "Error with details",
        details={"field": "username", "reason": "already_exists"}
    )
    assert exc.detail["details"] == {"field": "username", "reason": "already_exists"}