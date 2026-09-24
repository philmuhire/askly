from pydantic import BaseModel

class ErrorResponse(BaseModel):
    success: bool = False
    error: dict


class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 400
    ):
        self.message = message
        self.code = code
        self.status_code = status_code


class UserNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            message="User not found",
            code="USER_NOT_FOUND",
            status_code=404
        )

class DuplicateEmailException(AppException):
    def __init__(self):
        super().__init__(
            message="Email already exists",
            code="EMAIL_EXISTS",
            status_code=409
        )

class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid credentials",
            code="INVALID_CREDENTIALS",
            status_code=401
        )