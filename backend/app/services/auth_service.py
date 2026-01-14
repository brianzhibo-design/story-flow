# backend/app/services/auth_service.py
from datetime import datetime
from uuid import UUID
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserQuota, UserStatus, PlanType
from app.schemas.user import UserRegister, UserLogin, AuthResponse, UserOut, TokenOut
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from app.config import settings


class AuthService:
    """认证服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register(self, data: UserRegister) -> AuthResponse:
        """
        用户注册。
        
        Args:
            data: 注册数据
            
        Returns:
            认证响应（用户信息 + Token）
            
        Raises:
            UserAlreadyExistsError: 用户已存在
        """
        # 检查邮箱是否已注册
        existing = await self._get_user_by_email(data.email)
        if existing:
            raise UserAlreadyExistsError(f"Email {data.email} already registered")
        
        # 创建用户
        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            nickname=data.nickname,
        )
        self.db.add(user)
        await self.db.flush()
        
        # 创建默认配额
        quota = UserQuota(
            user_id=user.id,
            plan_type=PlanType.FREE,
            total_credits=100,
        )
        self.db.add(quota)
        await self.db.commit()
        await self.db.refresh(user)
        
        # 生成Token
        tokens = self._create_tokens(user.id)
        
        return AuthResponse(
            user=UserOut.model_validate(user),
            tokens=tokens,
        )
    
    async def login(self, data: UserLogin) -> AuthResponse:
        """
        用户登录。
        
        Args:
            data: 登录数据
            
        Returns:
            认证响应
            
        Raises:
            InvalidCredentialsError: 凭证无效
        """
        # 查找用户
        user = await self._get_user_by_email(data.email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")
        
        # 验证密码
        if not verify_password(data.password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")
        
        # 检查状态
        if user.status != UserStatus.ACTIVE:
            raise InvalidCredentialsError("Account is not active")
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        await self.db.commit()
        
        # 生成Token
        tokens = self._create_tokens(user.id)
        
        return AuthResponse(
            user=UserOut.model_validate(user),
            tokens=tokens,
        )
    
    async def refresh_token(self, refresh_token: str) -> TokenOut:
        """
        刷新Token。
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的Token对
        """
        # 验证刷新令牌
        user_id = verify_refresh_token(refresh_token)
        
        # 检查用户是否存在且活跃
        user = await self._get_user_by_id(UUID(user_id))
        if not user or user.status != UserStatus.ACTIVE:
            raise InvalidCredentialsError("Invalid refresh token")
        
        # 生成新Token
        return self._create_tokens(user.id)
    
    async def get_current_user(self, user_id: UUID) -> User:
        """
        获取当前用户。
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户对象
        """
        user = await self._get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user
    
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def _get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """通过ID获取用户"""
        # 将 UUID 转换为标准格式字符串（带连字符）
        user_id_str = str(user_id)
        result = await self.db.execute(
            select(User).where(User.id == user_id_str)
        )
        return result.scalar_one_or_none()
    
    def _create_tokens(self, user_id: UUID) -> TokenOut:
        """创建Token对"""
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        
        return TokenOut(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
