# backend/app/api/deps.py
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis, RedisClient
from app.core.security import verify_access_token
from app.core.exceptions import UnauthorizedError
from app.services.auth_service import AuthService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.models.user import User


async def get_token_from_header(
    authorization: str = Header(None, alias="Authorization")
) -> str:
    """从Header提取Token"""
    if not authorization:
        raise UnauthorizedError("Not authenticated")
    if not authorization.startswith("Bearer "):
        raise UnauthorizedError("Invalid authorization header format")
    return authorization[7:]


async def get_current_user_id(
    token: Annotated[str, Depends(get_token_from_header)]
) -> str:
    """获取当前用户ID（字符串格式）"""
    user_id = verify_access_token(token)
    return user_id


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> User:
    """获取当前用户对象"""
    auth_service = AuthService(db)
    try:
        # 将 UUID 格式标准化（确保带连字符）
        normalized_user_id = str(UUID(user_id))
        return await auth_service.get_current_user(UUID(normalized_user_id))
    except Exception:
        # 用户不存在时返回 401，触发前端重新登录
        raise UnauthorizedError("Token invalid or user not found")


# 类型别名
DBSession = Annotated[AsyncSession, Depends(get_db)]
Redis = Annotated[RedisClient, Depends(get_redis)]
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
CurrentUser = Annotated[User, Depends(get_current_user)]


# 服务依赖
def get_auth_service(db: DBSession) -> AuthService:
    return AuthService(db)


def get_project_service(db: DBSession) -> ProjectService:
    return ProjectService(db)


def get_task_service(db: DBSession) -> TaskService:
    return TaskService(db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
