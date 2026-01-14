# backend/app/models/user.py
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.subscription import UserSubscription


class UserRole(str, enum.Enum):
    """用户角色"""
    USER = "user"
    VIP = "vip"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    """用户状态"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class User(BaseModel):
    """用户模型"""
    
    __tablename__ = "users"
    
    # 基本信息
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    nickname: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    
    # 状态
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.USER,
        nullable=False,
    )
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus),
        default=UserStatus.ACTIVE,
        nullable=False,
    )
    
    # 验证
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # 登录
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # 关系
    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="user",
        lazy="selectin",
    )
    quota: Mapped[Optional["UserQuota"]] = relationship(
        "UserQuota",
        back_populates="user",
        uselist=False,
        lazy="selectin",
    )
    subscription: Mapped[Optional["UserSubscription"]] = relationship(
        "UserSubscription",
        back_populates="user",
        uselist=False,
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"


class PlanType(str, enum.Enum):
    """计划类型"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UserQuota(BaseModel):
    """用户配额"""
    
    __tablename__ = "user_quotas"
    
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    
    plan_type: Mapped[PlanType] = mapped_column(
        SQLEnum(PlanType),
        default=PlanType.FREE,
        nullable=False,
    )
    
    # 积分/额度
    total_credits: Mapped[int] = mapped_column(default=100)
    used_credits: Mapped[int] = mapped_column(default=0)
    
    # 重置时间
    reset_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # 关系
    user: Mapped["User"] = relationship(
        "User",
        back_populates="quota",
    )
    
    @property
    def remaining_credits(self) -> int:
        """剩余积分"""
        return max(0, self.total_credits - self.used_credits)
    
    def __repr__(self) -> str:
        return f"<UserQuota {self.user_id} {self.plan_type}>"
