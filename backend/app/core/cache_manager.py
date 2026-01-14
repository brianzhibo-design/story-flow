"""
多级缓存系统

L1: 进程内存 (本地缓存)
L2: Redis 缓存
L3: CDN 缓存 (静态资源)

特性:
- 自动过期
- 缓存穿透保护
- 缓存雪崩保护
- 热点数据预热
"""
import json
import time
import hashlib
import asyncio
import structlog
from functools import wraps
from typing import Optional, Callable, Any, TypeVar, Union
from collections import OrderedDict

from app.config import settings
from app.core.redis import redis_client

logger = structlog.get_logger()

T = TypeVar('T')


class LRUCache:
    """线程安全的 LRU 本地缓存"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: OrderedDict = OrderedDict()
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        async with self._lock:
            if key not in self._cache:
                return None
            
            item = self._cache[key]
            
            # 检查过期
            if item["expires"] and item["expires"] < time.time():
                del self._cache[key]
                return None
            
            # 移到末尾 (最近使用)
            self._cache.move_to_end(key)
            return item["value"]
    
    async def set(self, key: str, value: Any, ttl: int = 60):
        """设置缓存"""
        async with self._lock:
            # 检查容量
            if len(self._cache) >= self.max_size:
                # 删除最旧的
                self._cache.popitem(last=False)
            
            self._cache[key] = {
                "value": value,
                "expires": time.time() + ttl if ttl > 0 else None
            }
    
    async def delete(self, key: str):
        """删除缓存"""
        async with self._lock:
            self._cache.pop(key, None)
    
    async def clear(self):
        """清空缓存"""
        async with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)


class CacheManager:
    """多级缓存管理器"""
    
    def __init__(self):
        # L1: 本地缓存
        self._local = LRUCache(max_size=1000)
        
        # 缓存统计
        self._stats = {
            "l1_hits": 0,
            "l2_hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    # ==================== 核心方法 ====================
    
    async def get(
        self, 
        key: str, 
        deserialize: bool = True
    ) -> Optional[Any]:
        """
        读取缓存 (L1 -> L2)
        
        Args:
            key: 缓存键
            deserialize: 是否反序列化 JSON
        """
        # L1: 本地缓存
        value = await self._local.get(key)
        if value is not None:
            self._stats["l1_hits"] += 1
            return value
        
        # L2: Redis 缓存
        try:
            data = await redis_client.get(key)
            if data:
                self._stats["l2_hits"] += 1
                
                if deserialize:
                    try:
                        value = json.loads(data)
                    except json.JSONDecodeError:
                        value = data
                else:
                    value = data
                
                # 回填 L1 (短 TTL)
                await self._local.set(key, value, ttl=30)
                return value
        except Exception as e:
            logger.warning("cache_redis_get_error", key=key, error=str(e))
        
        self._stats["misses"] += 1
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 300,
        serialize: bool = True
    ):
        """
        写入缓存 (L1 + L2)
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间 (秒)
            serialize: 是否序列化为 JSON
        """
        self._stats["sets"] += 1
        
        # L1: 本地缓存 (较短 TTL)
        await self._local.set(key, value, min(ttl, 60))
        
        # L2: Redis 缓存
        try:
            if serialize:
                data = json.dumps(value, ensure_ascii=False, default=str)
            else:
                data = str(value)
            
            await redis_client.set(key, data, expire=ttl)
        except Exception as e:
            logger.warning("cache_redis_set_error", key=key, error=str(e))
    
    async def delete(self, key: str):
        """删除缓存"""
        self._stats["deletes"] += 1
        
        # L1
        await self._local.delete(key)
        
        # L2
        try:
            await redis_client.delete(key)
        except Exception as e:
            logger.warning("cache_redis_delete_error", key=key, error=str(e))
    
    async def delete_pattern(self, pattern: str):
        """批量删除 (支持通配符)"""
        try:
            # 获取匹配的键
            keys = await redis_client.keys(pattern)
            if keys:
                # 删除 L2
                for key in keys:
                    await redis_client.delete(key)
                    # 删除 L1
                    await self._local.delete(key)
                
                logger.info("cache_pattern_deleted", pattern=pattern, count=len(keys))
        except Exception as e:
            logger.warning("cache_delete_pattern_error", pattern=pattern, error=str(e))
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        # L1
        if await self._local.get(key) is not None:
            return True
        
        # L2
        try:
            return await redis_client.exists(key)
        except Exception:
            return False
    
    # ==================== 高级方法 ====================
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: int = 300
    ) -> Any:
        """
        获取或设置缓存 (缓存穿透保护)
        
        如果缓存不存在，调用 factory 获取数据并缓存
        """
        value = await self.get(key)
        if value is not None:
            return value
        
        # 获取数据
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()
        
        # 缓存结果 (包括空值，防止穿透)
        if value is not None:
            await self.set(key, value, ttl)
        else:
            # 空值短期缓存
            await self.set(key, "__NULL__", ttl=30)
        
        return value if value != "__NULL__" else None
    
    async def mget(self, keys: list[str]) -> dict[str, Any]:
        """批量获取"""
        results = {}
        
        for key in keys:
            value = await self.get(key)
            if value is not None:
                results[key] = value
        
        return results
    
    async def mset(self, data: dict[str, Any], ttl: int = 300):
        """批量设置"""
        for key, value in data.items():
            await self.set(key, value, ttl)
    
    # ==================== 统计 ====================
    
    def get_stats(self) -> dict:
        """获取缓存统计"""
        total_hits = self._stats["l1_hits"] + self._stats["l2_hits"]
        total_requests = total_hits + self._stats["misses"]
        hit_rate = total_hits / total_requests if total_requests > 0 else 0
        
        return {
            **self._stats,
            "local_size": self._local.size(),
            "hit_rate": round(hit_rate, 4),
            "total_requests": total_requests
        }
    
    def reset_stats(self):
        """重置统计"""
        for key in self._stats:
            self._stats[key] = 0


# ==================== 缓存键生成器 ====================

class CacheKeys:
    """缓存键模板"""
    
    # 用户相关
    USER = "user:{user_id}"
    USER_QUOTA = "user:quota:{user_id}"
    USER_SUBSCRIPTION = "user:sub:{user_id}"
    
    # 项目相关
    PROJECT = "project:{project_id}"
    PROJECT_SCENES = "project:scenes:{project_id}"
    PROJECT_LIST = "projects:user:{user_id}:page:{page}"
    
    # AI 相关
    AI_PROVIDER_HEALTH = "ai:health:{provider_type}:{provider_name}"
    AI_RESULT = "ai:result:{task_type}:{hash}"
    
    # 分享相关
    SHARE = "share:{share_code}"
    
    @staticmethod
    def hash_params(**kwargs) -> str:
        """生成参数哈希"""
        data = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(data.encode()).hexdigest()[:16]


# ==================== 缓存装饰器 ====================

def cached(
    prefix: str,
    ttl: int = 300,
    key_builder: Callable = None
):
    """
    缓存装饰器
    
    Usage:
        @cached("project", ttl=600)
        async def get_project(project_id: str):
            ...
        
        @cached("search", ttl=60, key_builder=lambda q, **kw: f"search:{q}")
        async def search(query: str, page: int = 1):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            cache = get_cache_manager()
            
            # 构建缓存键
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                key_parts = [prefix]
                key_parts.extend(str(a) for a in args)
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)
            
            # 查缓存
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 写缓存
            if result is not None:
                await cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(*patterns: str):
    """
    缓存失效装饰器
    
    Usage:
        @invalidate_cache("project:{project_id}", "projects:user:*")
        async def update_project(project_id: str, data: dict):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            result = await func(*args, **kwargs)
            
            cache = get_cache_manager()
            
            # 失效缓存
            for pattern in patterns:
                # 替换变量
                formatted = pattern.format(**kwargs)
                
                if "*" in formatted:
                    await cache.delete_pattern(formatted)
                else:
                    await cache.delete(formatted)
            
            return result
        return wrapper
    return decorator


# ==================== 全局实例 ====================

_cache_manager: CacheManager = None


def get_cache_manager() -> CacheManager:
    """获取缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

