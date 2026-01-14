"""
Redis 缓存服务
"""

import json
from typing import Any, Optional
from functools import wraps

from app.core.redis import redis_client


class CacheService:
    """缓存服务"""
    
    # 缓存前缀
    PREFIX = "storyflow:"
    
    # 默认过期时间
    DEFAULT_TTL = 3600  # 1小时
    
    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        """获取缓存"""
        data = await redis_client.get(f"{cls.PREFIX}{key}")
        if data:
            return json.loads(data)
        return None
    
    @classmethod
    async def set(cls, key: str, value: Any, ttl: int = None) -> bool:
        """设置缓存"""
        ttl = ttl or cls.DEFAULT_TTL
        return await redis_client.set(
            f"{cls.PREFIX}{key}",
            json.dumps(value, default=str),
            expire=ttl
        )
    
    @classmethod
    async def delete(cls, key: str) -> bool:
        """删除缓存"""
        return await redis_client.delete(f"{cls.PREFIX}{key}")
    
    @classmethod
    async def delete_pattern(cls, pattern: str) -> int:
        """按模式删除缓存"""
        if redis_client.client:
            keys = []
            async for key in redis_client.client.scan_iter(f"{cls.PREFIX}{pattern}"):
                keys.append(key)
            if keys:
                return await redis_client.client.delete(*keys)
        return 0
    
    @classmethod
    async def exists(cls, key: str) -> bool:
        """检查缓存是否存在"""
        return await redis_client.exists(f"{cls.PREFIX}{key}")


# 缓存 Key 定义
class CacheKeys:
    """缓存 Key 模板"""
    
    # 项目
    PROJECT = "project:{project_id}"
    PROJECT_ELEMENTS = "project:{project_id}:elements"
    PROJECT_SCENES = "project:{project_id}:scenes"
    
    # 元素
    ELEMENT = "element:{element_id}"
    ELEMENT_REFERENCE = "element:{element_id}:reference"
    
    # 用户
    USER = "user:{user_id}"
    USER_QUOTA = "user:{user_id}:quota"
    
    # AI 供应商
    PROVIDER_HEALTH = "provider:{type}:{name}:health"


# 缓存装饰器
def cached(key_template: str, ttl: int = 3600):
    """
    缓存装饰器
    
    Usage:
        @cached("project:{project_id}", ttl=1800)
        async def get_project(project_id: str): ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 构建缓存 key
            cache_key = key_template.format(**kwargs)
            
            # 尝试从缓存获取
            cached_value = await CacheService.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 调用原函数
            result = await func(*args, **kwargs)
            
            # 写入缓存
            if result is not None:
                await CacheService.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


# 缓存失效装饰器
def invalidate_cache(*key_templates: str):
    """
    缓存失效装饰器
    
    Usage:
        @invalidate_cache("project:{project_id}", "project:{project_id}:*")
        async def update_project(project_id: str, data: dict): ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # 删除相关缓存
            for template in key_templates:
                key = template.format(**kwargs)
                if "*" in key:
                    await CacheService.delete_pattern(key)
                else:
                    await CacheService.delete(key)
            
            return result
        return wrapper
    return decorator

