"""
用户配额服务

管理用户的 AI 调用配额
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.user import User, UserQuota, PlanType
from app.core.redis import redis_client
from app.core.exceptions import AIQuotaExceededError

# 类型别名：支持 str 或 UUID
UserIdType = Union[str, UUID]

logger = structlog.get_logger()


# 各套餐的配额配置
PLAN_QUOTAS = {
    PlanType.FREE: {
        "daily_credits": 10,           # 每日积分
        "monthly_credits": 100,        # 每月积分
        "max_projects": 3,             # 最大项目数
        "max_scenes_per_project": 10,  # 每项目最大分镜数
        "image_generation": 10,        # 每日图片生成次数
        "video_generation": 3,         # 每日视频生成次数
        "audio_generation": 5,         # 每日配音生成次数
    },
    PlanType.BASIC: {
        "daily_credits": 50,
        "monthly_credits": 500,
        "max_projects": 10,
        "max_scenes_per_project": 20,
        "image_generation": 50,
        "video_generation": 10,
        "audio_generation": 20,
    },
    PlanType.PRO: {
        "daily_credits": 100,
        "monthly_credits": 2000,
        "max_projects": 50,
        "max_scenes_per_project": 50,
        "image_generation": 100,
        "video_generation": 30,
        "audio_generation": 50,
    },
    PlanType.ENTERPRISE: {
        "daily_credits": 1000,
        "monthly_credits": 30000,
        "max_projects": -1,            # 无限制
        "max_scenes_per_project": 200,
        "image_generation": 1000,
        "video_generation": 300,
        "audio_generation": 500,
    },
}

# 操作消耗的积分
OPERATION_COSTS = {
    "storyboard": 1,           # 分镜生成
    "image_generation": 2,     # 图片生成
    "video_generation": 10,    # 视频生成
    "audio_generation": 1,     # 配音生成
    "compose": 5,              # 视频合成
}


class QuotaService:
    """用户配额服务"""
    
    CACHE_PREFIX = "quota:"
    CACHE_TTL = 300  # 5 分钟
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== 配额查询 ====================
    
    async def get_user_quota(self, user_id: UserIdType) -> UserQuota:
        """获取用户配额"""
        stmt = select(UserQuota).where(UserQuota.user_id == str(user_id))
        result = await self.db.execute(stmt)
        quota = result.scalar_one_or_none()
        
        if not quota:
            # 创建默认配额
            quota = await self._create_default_quota(user_id)
        
        return quota
    
    async def get_quota_status(self, user_id: UserIdType) -> dict:
        """
        获取用户配额状态
        
        Returns:
            {
                "plan": "free",
                "credits": {"used": 50, "total": 100, "remaining": 50},
                "daily_usage": {...},
                "limits": {...},
                "reset_at": "2024-01-01T00:00:00Z"
            }
        """
        quota = await self.get_user_quota(user_id)
        daily_usage = await self._get_daily_usage(user_id)
        plan_config = PLAN_QUOTAS[quota.plan_type]
        
        return {
            "plan": quota.plan_type.value,
            "credits": {
                "used": quota.used_credits,
                "total": quota.total_credits,
                "remaining": quota.total_credits - quota.used_credits
            },
            "daily_usage": daily_usage,
            "limits": plan_config,
            "reset_at": quota.reset_at.isoformat() if quota.reset_at else None
        }
    
    # ==================== 配额检查 ====================
    
    async def check_quota(
        self,
        user_id: UserIdType,
        operation: str,
        count: int = 1
    ) -> bool:
        """
        检查用户是否有足够的配额
        
        Args:
            user_id: 用户 ID
            operation: 操作类型 (image_generation, video_generation, etc.)
            count: 操作次数
        
        Returns:
            是否有足够配额
        """
        quota = await self.get_user_quota(user_id)
        cost = OPERATION_COSTS.get(operation, 1) * count
        
        # 检查总积分
        if quota.used_credits + cost > quota.total_credits:
            return False
        
        # 检查每日限额
        daily_usage = await self._get_daily_usage(user_id)
        plan_config = PLAN_QUOTAS[quota.plan_type]
        daily_limit_key = operation
        
        if daily_limit_key in plan_config:
            current_usage = daily_usage.get(operation, 0)
            if current_usage + count > plan_config[daily_limit_key]:
                return False
        
        return True
    
    async def require_quota(
        self,
        user_id: UserIdType,
        operation: str,
        count: int = 1
    ) -> None:
        """
        检查配额，不足时抛出异常
        """
        has_quota = await self.check_quota(user_id, operation, count)
        if not has_quota:
            quota_status = await self.get_quota_status(user_id)
            raise AIQuotaExceededError(
                message=f"配额不足，无法执行 {operation}",
                details=quota_status
            )
    
    # ==================== 配额消费 ====================
    
    async def consume_quota(
        self,
        user_id: UserIdType,
        operation: str,
        count: int = 1
    ) -> dict:
        """
        消费配额
        
        Returns:
            更新后的配额状态
        """
        quota = await self.get_user_quota(user_id)
        cost = OPERATION_COSTS.get(operation, 1) * count
        
        # 更新总积分
        quota.used_credits += cost
        
        # 更新每日使用量
        await self._increment_daily_usage(user_id, operation, count)
        
        await self.db.commit()
        
        logger.info(
            "quota_consumed",
            user_id=str(user_id),
            operation=operation,
            cost=cost,
            remaining=quota.total_credits - quota.used_credits
        )
        
        return await self.get_quota_status(user_id)
    
    async def refund_quota(
        self,
        user_id: UserIdType,
        operation: str,
        count: int = 1
    ) -> None:
        """
        退还配额（任务失败时使用）
        """
        quota = await self.get_user_quota(user_id)
        cost = OPERATION_COSTS.get(operation, 1) * count
        
        quota.used_credits = max(0, quota.used_credits - cost)
        await self._decrement_daily_usage(user_id, operation, count)
        
        await self.db.commit()
        
        logger.info(
            "quota_refunded",
            user_id=str(user_id),
            operation=operation,
            refund=cost
        )
    
    # ==================== 配额重置 ====================
    
    async def reset_monthly_quota(self, user_id: UserIdType) -> None:
        """重置月度配额"""
        quota = await self.get_user_quota(user_id)
        plan_config = PLAN_QUOTAS[quota.plan_type]
        
        quota.used_credits = 0
        quota.total_credits = plan_config["monthly_credits"]
        quota.reset_at = datetime.now(timezone.utc) + timedelta(days=30)
        
        await self.db.commit()
        
        logger.info("monthly_quota_reset", user_id=str(user_id))
    
    async def upgrade_plan(
        self,
        user_id: UserIdType,
        new_plan: PlanType
    ) -> UserQuota:
        """升级用户套餐"""
        quota = await self.get_user_quota(user_id)
        old_plan = quota.plan_type
        
        quota.plan_type = new_plan
        plan_config = PLAN_QUOTAS[new_plan]
        quota.total_credits = plan_config["monthly_credits"]
        quota.reset_at = datetime.now(timezone.utc) + timedelta(days=30)
        
        await self.db.commit()
        
        logger.info(
            "plan_upgraded",
            user_id=str(user_id),
            old_plan=old_plan.value,
            new_plan=new_plan.value
        )
        
        return quota
    
    # ==================== 私有方法 ====================
    
    async def _create_default_quota(self, user_id: UserIdType) -> UserQuota:
        """创建默认配额"""
        plan_config = PLAN_QUOTAS[PlanType.FREE]
        
        quota = UserQuota(
            user_id=str(user_id),
            plan_type=PlanType.FREE,
            total_credits=plan_config["monthly_credits"],
            used_credits=0,
            reset_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        self.db.add(quota)
        await self.db.commit()
        await self.db.refresh(quota)
        
        return quota
    
    async def _get_daily_usage(self, user_id: UserIdType) -> dict:
        """获取每日使用量（从 Redis）"""
        key = f"{self.CACHE_PREFIX}daily:{user_id}:{datetime.now(timezone.utc).date()}"
        data = await redis_client.get_json(key)
        return data or {}
    
    async def _increment_daily_usage(
        self,
        user_id: UserIdType,
        operation: str,
        count: int = 1
    ) -> None:
        """增加每日使用量"""
        key = f"{self.CACHE_PREFIX}daily:{user_id}:{datetime.now(timezone.utc).date()}"
        
        usage = await self._get_daily_usage(user_id)
        usage[operation] = usage.get(operation, 0) + count
        
        # 设置过期时间为第二天凌晨
        await redis_client.set_json(key, usage, ex=86400)
    
    async def _decrement_daily_usage(
        self,
        user_id: UserIdType,
        operation: str,
        count: int = 1
    ) -> None:
        """减少每日使用量"""
        key = f"{self.CACHE_PREFIX}daily:{user_id}:{datetime.now(timezone.utc).date()}"
        
        usage = await self._get_daily_usage(user_id)
        usage[operation] = max(0, usage.get(operation, 0) - count)
        
        await redis_client.set_json(key, usage, ex=86400)

