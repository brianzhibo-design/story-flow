# backend/app/core/exceptions.py
from typing import Any, Optional


class StoryFlowException(Exception):
    """应用异常基类"""
    
    code: int = 500
    message: str = "Internal Server Error"
    
    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[int] = None,
        details: Optional[Any] = None
    ):
        self.message = message or self.__class__.message
        self.code = code or self.__class__.code
        self.details = details
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        result = {
            "code": self.code,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result


# === 通用异常 (00xxx) ===
class ValidationError(StoryFlowException):
    """参数验证错误"""
    code = 400
    message = "Validation Error"


class UnauthorizedError(StoryFlowException):
    """未授权"""
    code = 401
    message = "Unauthorized"


class ForbiddenError(StoryFlowException):
    """禁止访问"""
    code = 403
    message = "Forbidden"


class NotFoundError(StoryFlowException):
    """资源不存在"""
    code = 404
    message = "Resource Not Found"


class ConflictError(StoryFlowException):
    """资源冲突"""
    code = 409
    message = "Resource Conflict"


class RateLimitError(StoryFlowException):
    """请求频率限制"""
    code = 429
    message = "Too Many Requests"


# === 用户模块异常 (01xxx) ===
class UserNotFoundError(NotFoundError):
    """用户不存在"""
    code = 1001
    message = "User Not Found"


class UserAlreadyExistsError(ConflictError):
    """用户已存在"""
    code = 1002
    message = "User Already Exists"


class InvalidCredentialsError(UnauthorizedError):
    """凭证无效"""
    code = 1003
    message = "Invalid Credentials"


class TokenExpiredError(UnauthorizedError):
    """Token过期"""
    code = 1004
    message = "Token Expired"


class TokenInvalidError(UnauthorizedError):
    """Token无效"""
    code = 1005
    message = "Invalid Token"


# === 项目模块异常 (02xxx) ===
class ProjectNotFoundError(NotFoundError):
    """项目不存在"""
    code = 2001
    message = "Project Not Found"


class ProjectAccessDeniedError(ForbiddenError):
    """无权访问项目"""
    code = 2002
    message = "Project Access Denied"


class StoryTextTooLongError(ValidationError):
    """故事文本过长"""
    code = 2003
    message = "Story Text Too Long"


# === 任务模块异常 (03xxx) ===
class TaskNotFoundError(NotFoundError):
    """任务不存在"""
    code = 3001
    message = "Task Not Found"


class TaskExecutionError(StoryFlowException):
    """任务执行失败"""
    code = 3002
    message = "Task Execution Failed"


class QuotaExceededError(ForbiddenError):
    """配额不足"""
    code = 3003
    message = "Quota Exceeded"


class AIQuotaExceededError(QuotaExceededError):
    """AI配额不足"""
    code = 3004
    message = "AI Quota Exceeded"


# === AI模块异常 (04xxx) ===
class AIProviderError(StoryFlowException):
    """AI供应商错误"""
    code = 4001
    message = "AI Provider Error"


class AIProviderUnavailableError(StoryFlowException):
    """AI供应商不可用"""
    code = 4002
    message = "AI Provider Unavailable"


class AIGenerationTimeoutError(StoryFlowException):
    """AI生成超时"""
    code = 4003
    message = "AI Generation Timeout"


# === 存储模块异常 (05xxx) ===
class StorageError(StoryFlowException):
    """存储错误"""
    code = 5001
    message = "Storage Error"


class FileNotFoundError(NotFoundError):
    """文件不存在"""
    code = 5002
    message = "File Not Found"


class FileTooLargeError(ValidationError):
    """文件过大"""
    code = 5003
    message = "File Too Large"
