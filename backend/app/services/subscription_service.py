"""
订阅管理服务

支持:
- 订阅计划管理
- 用户订阅操作
- 配额检查与消耗
- 使用量统计
"""
import structlog
from datetime import datetime, timedelta
from typing import Optional
from functools import wraps

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.subscription import (
    SubscriptionPlan, UserSubscription, UsageRecord, PaymentOrder,
    PlanType, BillingCycle, SubscriptionStatus, UsageType,
    SUBSCRIPTION_PLANS_CONFIG
)
from app.core.cache_manager import cached, get_cache_manager, CacheKeys

logger = structlog.get_logger()


class SubscriptionService:
    """订阅管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache = get_cache_manager()
    
    # ==================== 订阅计划 ====================
    
    async def get_all_plans(self) -> list[SubscriptionPlan]:
        """获取所有订阅计划"""
        stmt = (
            select(SubscriptionPlan)
            .where(SubscriptionPlan.is_active == True)
            .order_by(SubscriptionPlan.sort_order)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_plan(self, plan_type: PlanType) -> Optional[SubscriptionPlan]:
        """获取指定计划"""
        stmt = select(SubscriptionPlan).where(SubscriptionPlan.type == plan_type)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def init_plans(self):
        """初始化订阅计划 (数据库种子)"""
        for plan_type, config in SUBSCRIPTION_PLANS_CONFIG.items():
            existing = await self.get_plan(plan_type)
            if not existing:
                plan = SubscriptionPlan(
                    type=plan_type,
                    **config
                )
                self.db.add(plan)
        
        await self.db.commit()
        logger.info("subscription_plans_initialized")
    
    # ==================== 用户订阅 ====================
    
    async def get_user_subscription(self, user_id: str) -> Optional[UserSubscription]:
        """获取用户当前订阅"""
        cache_key = CacheKeys.USER_SUBSCRIPTION.format(user_id=user_id)
        
        # 查缓存
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        stmt = (
            select(UserSubscription)
            .where(UserSubscription.user_id == user_id)
            .where(UserSubscription.status == SubscriptionStatus.ACTIVE)
        )
        result = await self.db.execute(stmt)
        subscription = result.scalar_one_or_none()
        
        if subscription:
            await self.cache.set(cache_key, subscription, ttl=300)
        
        return subscription
    
    async def get_user_plan(self, user_id: str) -> SubscriptionPlan:
        """获取用户当前计划 (默认免费)"""
        subscription = await self.get_user_subscription(user_id)
        
        if subscription and subscription.plan:
            return subscription.plan
        
        # 返回免费计划
        plan = await self.get_plan(PlanType.FREE)
        
        # 如果计划不存在，创建一个默认的免费计划对象
        if not plan:
            # 尝试初始化计划
            await self.init_plans()
            plan = await self.get_plan(PlanType.FREE)
            
            # 如果仍然不存在，创建一个内存中的默认计划
            if not plan:
                plan = SubscriptionPlan(
                    id="default-free",
                    type=PlanType.FREE,
                    **SUBSCRIPTION_PLANS_CONFIG[PlanType.FREE]
                )
        
        return plan
    
    async def subscribe(
        self,
        user_id: str,
        plan_type: PlanType,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY
    ) -> UserSubscription:
        """创建/升级订阅"""
        plan = await self.get_plan(plan_type)
        if not plan:
            raise ValueError(f"计划 {plan_type} 不存在")
        
        # 检查现有订阅
        existing = await self.get_user_subscription(user_id)
        
        if existing:
            # 升级/降级
            existing.plan_id = plan.id
            existing.billing_cycle = billing_cycle
            existing.status = SubscriptionStatus.ACTIVE
            
            # 重新计算周期
            existing.current_period_start = datetime.utcnow()
            if billing_cycle == BillingCycle.YEARLY:
                existing.current_period_end = datetime.utcnow() + timedelta(days=365)
            else:
                existing.current_period_end = datetime.utcnow() + timedelta(days=30)
            
            subscription = existing
        else:
            # 新订阅
            period_end = datetime.utcnow() + (
                timedelta(days=365) if billing_cycle == BillingCycle.YEARLY 
                else timedelta(days=30)
            )
            
            subscription = UserSubscription(
                user_id=user_id,
                plan_id=plan.id,
                billing_cycle=billing_cycle,
                status=SubscriptionStatus.ACTIVE,
                current_period_start=datetime.utcnow(),
                current_period_end=period_end
            )
            self.db.add(subscription)
        
        await self.db.commit()
        
        # 清除缓存
        cache_key = CacheKeys.USER_SUBSCRIPTION.format(user_id=user_id)
        await self.cache.delete(cache_key)
        
        logger.info(
            "subscription_created",
            user_id=user_id,
            plan=plan_type.value,
            cycle=billing_cycle.value
        )
        
        return subscription
    
    async def cancel_subscription(
        self, 
        user_id: str, 
        reason: str = None
    ) -> UserSubscription:
        """取消订阅"""
        subscription = await self.get_user_subscription(user_id)
        
        if not subscription:
            raise ValueError("没有活跃的订阅")
        
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.utcnow()
        subscription.cancel_reason = reason
        subscription.auto_renew = False
        
        await self.db.commit()
        
        # 清除缓存
        cache_key = CacheKeys.USER_SUBSCRIPTION.format(user_id=user_id)
        await self.cache.delete(cache_key)
        
        logger.info("subscription_cancelled", user_id=user_id, reason=reason)
        
        return subscription


class QuotaService:
    """配额管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache = get_cache_manager()
        self.subscription_service = SubscriptionService(db)
    
    async def check_quota(
        self,
        user_id: str,
        usage_type: UsageType,
        amount: float = 1
    ) -> dict:
        """
        检查配额
        
        Returns:
            {
                "allowed": True/False,
                "remaining": 100,
                "limit": 200,
                "used": 100
            }
        """
        plan = await self.subscription_service.get_user_plan(user_id)
        subscription = await self.subscription_service.get_user_subscription(user_id)
        
        # 获取配额限制
        limit = self._get_limit(plan, usage_type)
        
        # 无限配额
        if limit == -1:
            return {"allowed": True, "remaining": -1, "limit": -1, "used": 0}
        
        # 获取当前周期使用量
        period_start = subscription.current_period_start if subscription else datetime.utcnow().replace(day=1)
        used = await self._get_period_usage(user_id, usage_type, period_start)
        
        remaining = limit - used
        allowed = remaining >= amount
        
        return {
            "allowed": allowed,
            "remaining": remaining,
            "limit": limit,
            "used": used
        }
    
    async def consume_quota(
        self,
        user_id: str,
        usage_type: UsageType,
        amount: float,
        project_id: str = None,
        task_id: str = None,
        cost: float = 0,
        extra_data: dict = None
    ) -> bool:
        """
        消耗配额
        
        Returns:
            是否成功消耗
        """
        # 检查配额
        quota = await self.check_quota(user_id, usage_type, amount)
        
        if not quota["allowed"]:
            logger.warning(
                "quota_exceeded",
                user_id=user_id,
                usage_type=usage_type.value,
                amount=amount,
                remaining=quota["remaining"]
            )
            return False
        
        # 记录使用
        await self.record_usage(
            user_id=user_id,
            usage_type=usage_type,
            amount=amount,
            project_id=project_id,
            task_id=task_id,
            cost=cost,
            extra_data=extra_data
        )
        
        return True
    
    async def record_usage(
        self,
        user_id: str,
        usage_type: UsageType,
        amount: float,
        project_id: str = None,
        task_id: str = None,
        cost: float = 0,
        extra_data: dict = None
    ):
        """记录使用量"""
        record = UsageRecord(
            user_id=user_id,
            usage_type=usage_type,
            amount=amount,
            unit=self._get_unit(usage_type),
            project_id=project_id,
            task_id=task_id,
            cost=cost,
            extra_data=extra_data or {}
        )
        
        self.db.add(record)
        await self.db.commit()
        
        logger.debug(
            "usage_recorded",
            user_id=user_id,
            type=usage_type.value,
            amount=amount
        )
    
    async def get_usage_summary(self, user_id: str) -> dict:
        """获取使用量摘要"""
        summary = {}
        
        for usage_type in UsageType:
            quota = await self.check_quota(user_id, usage_type)
            
            if quota["limit"] == -1:
                percentage = 0
            elif quota["limit"] > 0:
                percentage = (quota["used"] / quota["limit"]) * 100
            else:
                percentage = 0
            
            summary[usage_type.value] = {
                "used": quota["used"],
                "limit": quota["limit"],
                "remaining": quota["remaining"],
                "percentage": round(percentage, 1)
            }
        
        return summary
    
    async def get_usage_history(
        self,
        user_id: str,
        usage_type: UsageType = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> list[UsageRecord]:
        """获取使用记录"""
        stmt = select(UsageRecord).where(UsageRecord.user_id == user_id)
        
        if usage_type:
            stmt = stmt.where(UsageRecord.usage_type == usage_type)
        
        if start_date:
            stmt = stmt.where(UsageRecord.recorded_at >= start_date)
        
        if end_date:
            stmt = stmt.where(UsageRecord.recorded_at <= end_date)
        
        stmt = stmt.order_by(UsageRecord.recorded_at.desc()).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def _get_period_usage(
        self,
        user_id: str,
        usage_type: UsageType,
        period_start: datetime
    ) -> float:
        """获取周期内使用量"""
        stmt = (
            select(func.sum(UsageRecord.amount))
            .where(UsageRecord.user_id == user_id)
            .where(UsageRecord.usage_type == usage_type)
            .where(UsageRecord.recorded_at >= period_start)
        )
        
        result = await self.db.execute(stmt)
        total = result.scalar()
        
        return total or 0
    
    def _get_limit(self, plan: SubscriptionPlan, usage_type: UsageType) -> int:
        """获取配额限制"""
        mapping = {
            UsageType.LLM_TOKENS: plan.llm_tokens,
            UsageType.IMAGE_GEN: plan.image_count,
            UsageType.VIDEO_GEN: plan.video_count,
            UsageType.VIDEO_DURATION: plan.video_duration,
            UsageType.TTS: plan.tts_chars,
            UsageType.STORAGE: int(plan.storage_gb * 1024 * 1024 * 1024),  # 转为字节
        }
        return mapping.get(usage_type, 0)
    
    def _get_unit(self, usage_type: UsageType) -> str:
        """获取单位"""
        units = {
            UsageType.LLM_TOKENS: "tokens",
            UsageType.IMAGE_GEN: "count",
            UsageType.VIDEO_GEN: "count",
            UsageType.VIDEO_DURATION: "seconds",
            UsageType.TTS: "chars",
            UsageType.STORAGE: "bytes",
        }
        return units.get(usage_type, "count")


# ==================== 配额检查装饰器 ====================

def require_quota(usage_type: UsageType, amount: float = 1):
    """
    配额检查装饰器
    
    Usage:
        @require_quota(UsageType.IMAGE_GEN, 1)
        async def generate_image(request: Request, ...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从参数中获取必要信息
            request = kwargs.get("request")
            db = kwargs.get("db")
            current_user = kwargs.get("current_user")
            
            if not current_user:
                raise HTTPException(status_code=401, detail="未登录")
            
            if not db:
                raise HTTPException(status_code=500, detail="数据库会话不可用")
            
            # 检查配额
            quota_service = QuotaService(db)
            quota = await quota_service.check_quota(
                current_user.id, 
                usage_type, 
                amount
            )
            
            if not quota["allowed"]:
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "quota_exceeded",
                        "message": f"{usage_type.value} 配额不足",
                        "remaining": quota["remaining"],
                        "limit": quota["limit"]
                    }
                )
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 记录使用量 (成功后)
            await quota_service.record_usage(
                user_id=current_user.id,
                usage_type=usage_type,
                amount=amount
            )
            
            return result
        
        return wrapper
    return decorator


def check_feature(feature: str):
    """
    功能权限检查装饰器
    
    Usage:
        @check_feature("can_export_hd")
        async def export_hd(request: Request, ...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            db = kwargs.get("db")
            current_user = kwargs.get("current_user")
            
            if not current_user:
                raise HTTPException(status_code=401, detail="未登录")
            
            # 获取用户计划
            subscription_service = SubscriptionService(db)
            plan = await subscription_service.get_user_plan(current_user.id)
            
            # 检查功能权限
            has_feature = getattr(plan, feature, False)
            
            if not has_feature:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "feature_not_available",
                        "message": f"您的订阅计划不支持此功能",
                        "feature": feature,
                        "current_plan": plan.type.value
                    }
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

