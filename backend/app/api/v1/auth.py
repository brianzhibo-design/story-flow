# backend/app/api/v1/auth.py
from fastapi import APIRouter, status

from app.api.deps import AuthServiceDep, CurrentUser
from app.schemas.user import (
    UserRegister,
    UserLogin,
    TokenRefresh,
    AuthResponse,
    TokenOut,
    UserOut,
)
from app.schemas.base import BaseResponse

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post(
    "/register",
    response_model=BaseResponse[AuthResponse],
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
)
async def register(
    data: UserRegister,
    auth_service: AuthServiceDep,
):
    """
    用户注册接口。
    
    - **email**: 邮箱地址
    - **password**: 密码（至少8位，包含字母和数字）
    - **nickname**: 昵称（可选）
    """
    result = await auth_service.register(data)
    return BaseResponse(data=result)


@router.post(
    "/login",
    response_model=BaseResponse[AuthResponse],
    summary="用户登录",
)
async def login(
    data: UserLogin,
    auth_service: AuthServiceDep,
):
    """
    用户登录接口。
    
    - **email**: 邮箱地址
    - **password**: 密码
    """
    result = await auth_service.login(data)
    return BaseResponse(data=result)


@router.post(
    "/refresh",
    response_model=BaseResponse[TokenOut],
    summary="刷新Token",
)
async def refresh_token(
    data: TokenRefresh,
    auth_service: AuthServiceDep,
):
    """
    刷新访问令牌。
    
    - **refresh_token**: 刷新令牌
    """
    result = await auth_service.refresh_token(data.refresh_token)
    return BaseResponse(data=result)


@router.get(
    "/me",
    response_model=BaseResponse[UserOut],
    summary="获取当前用户",
)
async def get_me(current_user: CurrentUser):
    """获取当前登录用户信息。"""
    return BaseResponse(data=UserOut.model_validate(current_user))
