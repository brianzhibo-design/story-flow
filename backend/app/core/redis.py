# backend/app/core/redis.py
from typing import Optional, Any
import redis.asyncio as redis
from redis.asyncio import ConnectionPool, Redis
import json

from app.config import settings


class RedisClient:
    """Redis 客户端封装"""
    
    def __init__(self):
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[Redis] = None
    
    async def connect(self) -> None:
        """建立连接"""
        self.pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=20,
            decode_responses=True,
        )
        self.client = Redis(connection_pool=self.pool)
    
    async def disconnect(self) -> None:
        """断开连接"""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()
    
    async def get(self, key: str) -> Optional[str]:
        """获取值"""
        return await self.client.get(key)
    
    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """设置值"""
        return await self.client.set(key, value, ex=expire)
    
    async def delete(self, key: str) -> int:
        """删除键"""
        return await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self.client.exists(key) > 0
    
    async def get_json(self, key: str) -> Optional[Any]:
        """获取JSON值"""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set_json(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """设置JSON值"""
        return await self.set(key, json.dumps(value), expire)
    
    async def incr(self, key: str) -> int:
        """自增"""
        return await self.client.incr(key)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        return await self.client.expire(key, seconds)
    
    async def publish(self, channel: str, message: str) -> int:
        """发布消息"""
        return await self.client.publish(channel, message)
    
    # 分布式锁
    async def acquire_lock(
        self,
        lock_name: str,
        expire: int = 10
    ) -> bool:
        """获取分布式锁"""
        return await self.client.set(
            f"lock:{lock_name}",
            "1",
            nx=True,
            ex=expire
        )
    
    async def release_lock(self, lock_name: str) -> None:
        """释放分布式锁"""
        await self.delete(f"lock:{lock_name}")


# 全局实例
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """获取Redis客户端依赖"""
    return redis_client
