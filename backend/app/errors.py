from enum import Enum
from typing import Any, Optional
from fastapi import HTTPException, status

class ErrorCode(str, Enum):
    AUTH_FAILED = "auth_failed"
    INVALID_CREDENTIALS = "invalid_credentials"
    EMAIL_ALREADY_EXISTS = "email_already_exists"
    INSUFFICIENT_CREDITS = "insufficient_credits"
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"
    PROCESSING_FAILED = "processing_failed"
    INTERNAL_SERVER_ERROR = "internal_server_error"

class AppBaseException(HTTPException):
    def __init__(
        self,
        status_code: int,
        error_code: ErrorCode,
        detail: str,
        metadata: Optional[dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail={
            "error_code": error_code,
            "message": detail,
            "metadata": metadata or {}
        })

class AuthError(AppBaseException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, ErrorCode.AUTH_FAILED, detail)

class CreditError(AppBaseException):
    def __init__(self, detail: str = "Insufficient credits"):
        super().__init__(status.HTTP_403_FORBIDDEN, ErrorCode.INSUFFICIENT_CREDITS, detail)

class NotFoundError(AppBaseException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, ErrorCode.NOT_FOUND, detail)
