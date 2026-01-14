# backend/app/schemas/user.py
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

from app.models.user import UserRole, UserStatus, PlanType


# === 请求模式 ===

class UserRegister(BaseModel):
    """用户注册请求"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    nickname: Optional[str] = Field(None, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("密码必须包含字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含数字")
        return v


class UserLogin(BaseModel):
    """用户登录请求"""
    email: EmailStr
    password: str


class TokenRefresh(BaseModel):
    """刷新Token请求"""
    refresh_token: str


class UserUpdate(BaseModel):
    """用户信息更新"""
    nickname: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)


class PasswordChange(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("密码必须包含字母")
        if not re.search(r"\d", v):
            raise ValueError("密码必须包含数字")
        return v


# === 响应模式 ===

class UserOut(BaseModel):
    """用户信息输出"""
    id: UUID
    email: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole
    status: UserStatus
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class UserQuotaOut(BaseModel):
    """用户配额输出"""
    plan_type: PlanType
    total_credits: int
    used_credits: int
    remaining_credits: int
    reset_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class UserWithQuota(UserOut):
    """带配额的用户信息"""
    quota: Optional[UserQuotaOut] = None


class TokenOut(BaseModel):
    """Token输出"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    """认证响应"""
    user: UserOut
    tokens: TokenOut
