from fastapi import HTTPException, status
from typing import Optional, Dict, Any


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message, "details": details or {}}
        )


class BadRequestException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(status.HTTP_400_BAD_REQUEST, "BAD_REQUEST", message, details)


class NotFoundException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(status.HTTP_404_NOT_FOUND, "NOT_FOUND", message, details)


class UnauthorizedException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(status.HTTP_401_UNAUTHORIZED, "UNAUTHORIZED", message, details)


class ForbiddenException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(status.HTTP_403_FORBIDDEN, "FORBIDDEN", message, details)


class ConflictException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(status.HTTP_409_CONFLICT, "CONFLICT", message, details)


class ValidationException(AppException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, "VALIDATION_ERROR", message, details)