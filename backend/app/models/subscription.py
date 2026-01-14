"""
会员订阅模型

支持:
- 多级订阅计划
- 使用量追踪
- 自动续费
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import Optional
import enum

from app.models.base import Base, TimestampMixin, UUIDMixin, JSONB


class PlanType(enum.Enum):
    """订阅计划类型"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class BillingCycle(enum.Enum):
    """计费周期"""
    MONTHLY = "monthly"
    YEARLY = "yearly"


class SubscriptionStatus(enum.Enum):
    """订阅状态"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"
    TRIAL = "trial"


class PaymentMethod(enum.Enum):
    """支付方式"""
    ALIPAY = "alipay"
    WECHAT = "wechat"
    CREDIT_CARD = "credit_card"


class UsageType(enum.Enum):
    """使用类型"""
    LLM_TOKENS = "llm_tokens"
    IMAGE_GEN = "image_gen"
    VIDEO_GEN = "video_gen"
    VIDEO_DURATION = "video_duration"
    TTS = "tts"
    STORAGE = "storage"


class SubscriptionPlan(Base, UUIDMixin, TimestampMixin):
    """订阅计划"""
    __tablename__ = "subscription_plans"
    
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[PlanType] = mapped_column(SQLEnum(PlanType), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 价格 (人民币)
    price_monthly: Mapped[float] = mapped_column(Float, default=0)
    price_yearly: Mapped[float] = mapped_column(Float, default=0)
    
    # 项目限制
    projects_limit: Mapped[int] = mapped_column(Integer, default=3)
    scenes_per_project: Mapped[int] = mapped_column(Integer, default=20)
    storage_gb: Mapped[float] = mapped_column(Float, default=1)
    
    # AI 调用配额 (每月)
    llm_tokens: Mapped[int] = mapped_column(Integer, default=100000)
    image_count: Mapped[int] = mapped_column(Integer, default=50)
    video_count: Mapped[int] = mapped_column(Integer, default=10)
    video_duration: Mapped[int] = mapped_column(Integer, default=50)  # 秒
    tts_chars: Mapped[int] = mapped_column(Integer, default=10000)  # 字符数
    
    # 功能权限
    can_export_hd: Mapped[bool] = mapped_column(Boolean, default=False)
    can_remove_watermark: Mapped[bool] = mapped_column(Boolean, default=False)
    can_use_premium_voices: Mapped[bool] = mapped_column(Boolean, default=False)
    can_collaborate: Mapped[bool] = mapped_column(Boolean, default=False)
    priority_queue: Mapped[bool] = mapped_column(Boolean, default=False)
    api_access: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 高级功能
    features: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class UserSubscription(Base, UUIDMixin, TimestampMixin):
    """用户订阅"""
    __tablename__ = "user_subscriptions"
    
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("subscription_plans.id"), nullable=False)
    
    status: Mapped[SubscriptionStatus] = mapped_column(
        SQLEnum(SubscriptionStatus), 
        default=SubscriptionStatus.ACTIVE
    )
    
    # 计费周期
    billing_cycle: Mapped[BillingCycle] = mapped_column(
        SQLEnum(BillingCycle), 
        default=BillingCycle.MONTHLY
    )
    current_period_start: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    current_period_end: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # 支付信息
    payment_method: Mapped[Optional[PaymentMethod]] = mapped_column(
        SQLEnum(PaymentMethod), 
        nullable=True
    )
    last_payment_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_payment_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 自动续费
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 取消信息
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancel_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # 试用期
    trial_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 关系
    user = relationship("User", back_populates="subscription")
    plan = relationship("SubscriptionPlan")


class UsageRecord(Base, TimestampMixin):
    """使用量记录"""
    __tablename__ = "usage_records"
    
    # 手动定义 ID 避免与 SQLAlchemy metadata 冲突
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # 使用类型
    usage_type: Mapped[UsageType] = mapped_column(SQLEnum(UsageType), nullable=False)
    
    # 使用量
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="count")
    
    # 关联
    project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("projects.id"), nullable=True)
    task_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # 成本 (用于计算实际消耗)
    cost: Mapped[float] = mapped_column(Float, default=0)
    
    # 额外数据 - 使用 nullable 而不是 default 避免可变默认值问题
    extra_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # 记录时间 (按月汇总用)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class PaymentOrder(Base, UUIDMixin, TimestampMixin):
    """支付订单"""
    __tablename__ = "payment_orders"
    
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    
    # 订单信息
    order_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    plan_type: Mapped[PlanType] = mapped_column(SQLEnum(PlanType), nullable=False)
    billing_cycle: Mapped[BillingCycle] = mapped_column(SQLEnum(BillingCycle), nullable=False)
    
    # 金额
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="CNY")
    
    # 支付
    payment_method: Mapped[Optional[PaymentMethod]] = mapped_column(
        SQLEnum(PaymentMethod), 
        nullable=True
    )
    payment_status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/paid/failed/refunded
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 第三方支付信息
    external_order_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    payment_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # 发票
    invoice_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    invoice_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    user = relationship("User")


# ==================== 计划配置 ====================

SUBSCRIPTION_PLANS_CONFIG = {
    PlanType.FREE: {
        "name": "免费版",
        "price_monthly": 0,
        "price_yearly": 0,
        "projects_limit": 3,
        "scenes_per_project": 10,
        "storage_gb": 0.5,
        "llm_tokens": 50000,
        "image_count": 20,
        "video_count": 5,
        "video_duration": 25,
        "tts_chars": 5000,
        "can_export_hd": False,
        "can_remove_watermark": False,
        "can_use_premium_voices": False,
        "can_collaborate": False,
        "priority_queue": False,
        "api_access": False,
    },
    PlanType.BASIC: {
        "name": "基础版",
        "price_monthly": 29,
        "price_yearly": 290,
        "projects_limit": 10,
        "scenes_per_project": 30,
        "storage_gb": 5,
        "llm_tokens": 500000,
        "image_count": 200,
        "video_count": 50,
        "video_duration": 250,
        "tts_chars": 50000,
        "can_export_hd": True,
        "can_remove_watermark": False,
        "can_use_premium_voices": False,
        "can_collaborate": False,
        "priority_queue": False,
        "api_access": False,
    },
    PlanType.PRO: {
        "name": "专业版",
        "price_monthly": 99,
        "price_yearly": 990,
        "projects_limit": 50,
        "scenes_per_project": 100,
        "storage_gb": 50,
        "llm_tokens": 2000000,
        "image_count": 1000,
        "video_count": 200,
        "video_duration": 1000,
        "tts_chars": 200000,
        "can_export_hd": True,
        "can_remove_watermark": True,
        "can_use_premium_voices": True,
        "can_collaborate": True,
        "priority_queue": True,
        "api_access": False,
    },
    PlanType.ENTERPRISE: {
        "name": "企业版",
        "price_monthly": 0,  # 联系销售
        "price_yearly": 0,
        "projects_limit": -1,  # 无限
        "scenes_per_project": -1,
        "storage_gb": 500,
        "llm_tokens": -1,
        "image_count": -1,
        "video_count": -1,
        "video_duration": -1,
        "tts_chars": -1,
        "can_export_hd": True,
        "can_remove_watermark": True,
        "can_use_premium_voices": True,
        "can_collaborate": True,
        "priority_queue": True,
        "api_access": True,
    },
}

