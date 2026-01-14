# backend/app/schemas/__init__.py
"""
Pydantic 模式模块。
"""

from app.schemas.base import (
    BaseResponse,
    ErrorResponse,
    ErrorDetail,
    PaginatedResponse,
    PaginatedData,
    PaginationMeta,
    ResponseMeta,
    success_response,
    error_response,
    paginated_response,
)
from app.schemas.user import (
    UserRegister,
    UserLogin,
    TokenRefresh,
    UserUpdate,
    PasswordChange,
    UserOut,
    UserQuotaOut,
    UserWithQuota,
    TokenOut,
    AuthResponse,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectGenerate,
    CharacterOut,
    ProjectOut,
    ProjectDetail,
    ProjectListItem,
    GenerateResponse,
)
from app.schemas.scene import (
    SceneCreate,
    SceneUpdate,
    SceneRegenerate,
    SceneBatchCreate,
    SceneOut,
    SceneListOut,
)
from app.schemas.task import (
    TaskOut,
    TaskDetail,
    TaskListOut,
    TaskProgress,
)

__all__ = [
    # Base
    "BaseResponse",
    "ErrorResponse",
    "ErrorDetail",
    "PaginatedResponse",
    "PaginatedData",
    "PaginationMeta",
    "ResponseMeta",
    "success_response",
    "error_response",
    "paginated_response",
    # User
    "UserRegister",
    "UserLogin",
    "TokenRefresh",
    "UserUpdate",
    "PasswordChange",
    "UserOut",
    "UserQuotaOut",
    "UserWithQuota",
    "TokenOut",
    "AuthResponse",
    # Project
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectGenerate",
    "CharacterOut",
    "ProjectOut",
    "ProjectDetail",
    "ProjectListItem",
    "GenerateResponse",
    # Scene
    "SceneCreate",
    "SceneUpdate",
    "SceneRegenerate",
    "SceneBatchCreate",
    "SceneOut",
    "SceneListOut",
    # Task
    "TaskOut",
    "TaskDetail",
    "TaskListOut",
    "TaskProgress",
]
