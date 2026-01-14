"""
限流器单元测试
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import time

from app.core.rate_limiter import (
    RateLimiter,
    GLOBAL_LIMITER,
    AUTH_LIMITER,
    AI_GENERATION_LIMITER,
)


class TestRateLimiter:
    """限流器测试"""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_allows_under_limit(self):
        """测试未达到限制时允许请求"""
        limiter = RateLimiter(requests=10, window=60, key_prefix="test")
        
        # 模拟 Redis 操作
        mock_pipeline = MagicMock()
        mock_pipeline.zremrangebyscore = MagicMock()
        mock_pipeline.zcard = MagicMock()
        mock_pipeline.zadd = MagicMock()
        mock_pipeline.expire = MagicMock()
        mock_pipeline.execute = AsyncMock(return_value=[0, 5, 1, True])  # 5 个请求
        
        with patch('app.core.rate_limiter.redis_client') as mock_redis:
            mock_redis.client = MagicMock()
            mock_redis.client.pipeline = MagicMock(return_value=mock_pipeline)
            mock_redis.connect = AsyncMock()
            
            is_allowed, info = await limiter.is_allowed("test_key")
        
        assert is_allowed is True
        assert info["remaining"] == 4  # 10 - 5 - 1
        assert info["limit"] == 10
    
    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_over_limit(self):
        """测试超过限制时拒绝请求"""
        limiter = RateLimiter(requests=10, window=60, key_prefix="test")
        
        mock_pipeline = MagicMock()
        mock_pipeline.zremrangebyscore = MagicMock()
        mock_pipeline.zcard = MagicMock()
        mock_pipeline.zadd = MagicMock()
        mock_pipeline.expire = MagicMock()
        mock_pipeline.execute = AsyncMock(return_value=[0, 10, 1, True])  # 已达到限制
        
        with patch('app.core.rate_limiter.redis_client') as mock_redis:
            mock_redis.client = MagicMock()
            mock_redis.client.pipeline = MagicMock(return_value=mock_pipeline)
            mock_redis.connect = AsyncMock()
            
            is_allowed, info = await limiter.is_allowed("test_key")
        
        assert is_allowed is False
        assert info["remaining"] == 0
    
    def test_predefined_limiters_exist(self):
        """测试预定义限流器存在"""
        assert GLOBAL_LIMITER is not None
        assert AUTH_LIMITER is not None
        assert AI_GENERATION_LIMITER is not None
    
    def test_auth_limiter_stricter(self):
        """测试认证限流器更严格"""
        assert AUTH_LIMITER.requests < GLOBAL_LIMITER.requests
    
    def test_ai_limiter_stricter(self):
        """测试 AI 限流器更严格"""
        assert AI_GENERATION_LIMITER.requests < GLOBAL_LIMITER.requests
    
    @pytest.mark.asyncio
    async def test_reset_limiter(self):
        """测试重置限流计数"""
        limiter = RateLimiter(requests=10, window=60, key_prefix="test")
        
        with patch('app.core.rate_limiter.redis_client') as mock_redis:
            mock_redis.delete = AsyncMock(return_value=1)
            
            await limiter.reset("test_key")
            
            mock_redis.delete.assert_called_once()

