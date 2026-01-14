"""
配额服务单元测试
"""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.services.quota_service import QuotaService, PLAN_QUOTAS, OPERATION_COSTS
from app.models.user import PlanType
from app.core.exceptions import AIQuotaExceededError


class TestQuotaConfig:
    """配额配置测试"""
    
    def test_plan_quotas_defined(self):
        """测试套餐配额已定义"""
        assert PlanType.FREE in PLAN_QUOTAS
        assert PlanType.PREMIUM in PLAN_QUOTAS
        assert PlanType.ENTERPRISE in PLAN_QUOTAS
    
    def test_free_plan_limits(self):
        """测试免费版限制"""
        free = PLAN_QUOTAS[PlanType.FREE]
        
        assert free["daily_credits"] == 10
        assert free["monthly_credits"] == 100
        assert free["max_projects"] == 3
    
    def test_premium_higher_than_free(self):
        """测试专业版配额高于免费版"""
        free = PLAN_QUOTAS[PlanType.FREE]
        premium = PLAN_QUOTAS[PlanType.PREMIUM]
        
        assert premium["monthly_credits"] > free["monthly_credits"]
        assert premium["max_projects"] > free["max_projects"]
        assert premium["image_generation"] > free["image_generation"]
    
    def test_operation_costs_defined(self):
        """测试操作消耗已定义"""
        assert "image_generation" in OPERATION_COSTS
        assert "video_generation" in OPERATION_COSTS
        assert OPERATION_COSTS["video_generation"] > OPERATION_COSTS["image_generation"]


class TestQuotaService:
    """配额服务测试"""
    
    @pytest.mark.asyncio
    async def test_check_quota_sufficient(self, db_session, test_user):
        """测试配额充足时检查通过"""
        service = QuotaService(db_session)
        
        # 模拟 Redis
        with patch.object(service, '_get_daily_usage', return_value={}):
            result = await service.check_quota(
                test_user.id, 
                "image_generation", 
                count=1
            )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_quota_exceeded(self, db_session, test_user):
        """测试配额超限时检查失败"""
        service = QuotaService(db_session)
        
        # 先消耗所有配额
        quota = await service.get_user_quota(test_user.id)
        quota.used_credits = quota.total_credits
        await db_session.commit()
        
        with patch.object(service, '_get_daily_usage', return_value={}):
            result = await service.check_quota(
                test_user.id,
                "image_generation",
                count=1
            )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_require_quota_raises_exception(self, db_session, test_user):
        """测试配额不足时抛出异常"""
        service = QuotaService(db_session)
        
        # 消耗所有配额
        quota = await service.get_user_quota(test_user.id)
        quota.used_credits = quota.total_credits
        await db_session.commit()
        
        with patch.object(service, '_get_daily_usage', return_value={}):
            with pytest.raises(AIQuotaExceededError):
                await service.require_quota(
                    test_user.id,
                    "image_generation"
                )
    
    @pytest.mark.asyncio
    async def test_consume_quota(self, db_session, test_user):
        """测试消费配额"""
        service = QuotaService(db_session)
        
        initial_quota = await service.get_user_quota(test_user.id)
        initial_used = initial_quota.used_credits
        
        with patch.object(service, '_get_daily_usage', return_value={}):
            with patch.object(service, '_increment_daily_usage', new_callable=AsyncMock):
                await service.consume_quota(
                    test_user.id,
                    "image_generation",
                    count=1
                )
        
        await db_session.refresh(initial_quota)
        
        expected_cost = OPERATION_COSTS["image_generation"]
        assert initial_quota.used_credits == initial_used + expected_cost
    
    @pytest.mark.asyncio
    async def test_refund_quota(self, db_session, test_user):
        """测试退还配额"""
        service = QuotaService(db_session)
        
        # 先消费一些配额
        quota = await service.get_user_quota(test_user.id)
        quota.used_credits = 10
        await db_session.commit()
        
        with patch.object(service, '_decrement_daily_usage', new_callable=AsyncMock):
            await service.refund_quota(
                test_user.id,
                "image_generation",
                count=1
            )
        
        await db_session.refresh(quota)
        
        expected_cost = OPERATION_COSTS["image_generation"]
        assert quota.used_credits == 10 - expected_cost
    
    @pytest.mark.asyncio
    async def test_upgrade_plan(self, db_session, test_user):
        """测试升级套餐"""
        service = QuotaService(db_session)
        
        quota = await service.upgrade_plan(test_user.id, PlanType.PREMIUM)
        
        assert quota.plan_type == PlanType.PREMIUM
        assert quota.total_credits == PLAN_QUOTAS[PlanType.PREMIUM]["monthly_credits"]
    
    @pytest.mark.asyncio
    async def test_get_quota_status(self, db_session, test_user):
        """测试获取配额状态"""
        service = QuotaService(db_session)
        
        with patch.object(service, '_get_daily_usage', return_value={"image_generation": 5}):
            status = await service.get_quota_status(test_user.id)
        
        assert "plan" in status
        assert "credits" in status
        assert "daily_usage" in status
        assert "limits" in status
        assert status["daily_usage"]["image_generation"] == 5

