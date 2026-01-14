"""
API 限流器

基于 Redis 的滑动窗口限流实现
"""

import time
from typing import Optional
from functools import wraps

from fastapi import Request, HTTPException, status
import structlog

from app.core.redis import redis_client

logger = structlog.get_logger()


class RateLimiter:
    """
    滑动窗口限流器
    
    支持按用户、IP、API 端点进行限流
    """
    
    PREFIX = "ratelimit:"
    
    def __init__(
        self,
        requests: int,
        window: int,
        key_prefix: str = ""
    ):
        """
        初始化限流器
        
        Args:
            requests: 窗口内允许的最大请求数
            window: 时间窗口（秒）
            key_prefix: 键前缀，用于区分不同的限流规则
        """
        self.requests = requests
        self.window = window
        self.key_prefix = key_prefix
    
    async def is_allowed(self, key: str) -> tuple[bool, dict]:
        """
        检查请求是否被允许
        
        Returns:
            (是否允许, {remaining: 剩余次数, reset: 重置时间})
        """
        full_key = f"{self.PREFIX}{self.key_prefix}:{key}"
        now = time.time()
        window_start = now - self.window
        
        if not redis_client.client:
            await redis_client.connect()
        
        pipe = redis_client.client.pipeline()
        
        # 移除过期的请求记录
        pipe.zremrangebyscore(full_key, 0, window_start)
        # 获取当前窗口内的请求数
        pipe.zcard(full_key)
        # 添加当前请求
        pipe.zadd(full_key, {str(now): now})
        # 设置过期时间
        pipe.expire(full_key, self.window)
        
        results = await pipe.execute()
        request_count = results[1]
        
        remaining = max(0, self.requests - request_count - 1)
        reset_time = int(now + self.window)
        
        is_allowed = request_count < self.requests
        
        if not is_allowed:
            logger.warning(
                "rate_limit_exceeded",
                key=key,
                limit=self.requests,
                window=self.window
            )
        
        return is_allowed, {
            "remaining": remaining,
            "limit": self.requests,
            "reset": reset_time
        }
    
    async def reset(self, key: str) -> None:
        """重置限流计数"""
        full_key = f"{self.PREFIX}{self.key_prefix}:{key}"
        await redis_client.delete(full_key)


# ==================== 预定义限流规则 ====================

# API 全局限流：每分钟 60 次
GLOBAL_LIMITER = RateLimiter(requests=60, window=60, key_prefix="global")

# 认证限流：每分钟 10 次（防止暴力破解）
AUTH_LIMITER = RateLimiter(requests=10, window=60, key_prefix="auth")

# AI 生成限流：每分钟 5 次
AI_GENERATION_LIMITER = RateLimiter(requests=5, window=60, key_prefix="ai")

# 文件上传限流：每分钟 20 次
UPLOAD_LIMITER = RateLimiter(requests=20, window=60, key_prefix="upload")


# ==================== 限流装饰器 ====================

def rate_limit(
    limiter: RateLimiter,
    key_func=None
):
    """
    限流装饰器
    
    Usage:
        @router.post("/login")
        @rate_limit(AUTH_LIMITER, key_func=lambda req: req.client.host)
        async def login(request: Request, ...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取 request
            request: Request = kwargs.get("request")
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if request is None:
                return await func(*args, **kwargs)
            
            # 生成限流 key
            if key_func:
                key = key_func(request)
            else:
                # 默认按用户 ID 或 IP
                user = getattr(request.state, "user", None)
                if user:
                    key = f"user:{user.id}"
                else:
                    key = f"ip:{request.client.host}"
            
            # 检查限流
            is_allowed, info = await limiter.is_allowed(key)
            
            # 添加响应头
            # 这些头在 middleware 中添加
            request.state.rate_limit_info = info
            
            if not is_allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "message": "Too many requests",
                        "retry_after": info["reset"] - int(time.time())
                    },
                    headers={
                        "X-RateLimit-Limit": str(info["limit"]),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(info["reset"]),
                        "Retry-After": str(info["reset"] - int(time.time()))
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ==================== 限流中间件 ====================

class RateLimitMiddleware:
    """
    全局限流中间件
    """
    
    def __init__(self, app, limiter: RateLimiter = GLOBAL_LIMITER):
        self.app = app
        self.limiter = limiter
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        from starlette.requests import Request
        request = Request(scope, receive, send)
        
        # 跳过健康检查等路径
        if request.url.path in ["/health", "/metrics", "/docs", "/openapi.json"]:
            await self.app(scope, receive, send)
            return
        
        # 生成 key
        user_id = scope.get("state", {}).get("user_id")
        if user_id:
            key = f"user:{user_id}"
        else:
            client = scope.get("client")
            key = f"ip:{client[0]}" if client else "unknown"
        
        is_allowed, info = await self.limiter.is_allowed(key)
        
        if not is_allowed:
            from starlette.responses import JSONResponse
            response = JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info["reset"]),
                }
            )
            await response(scope, receive, send)
            return
        
        # 添加限流信息到响应头
        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend([
                    (b"x-ratelimit-limit", str(info["limit"]).encode()),
                    (b"x-ratelimit-remaining", str(info["remaining"]).encode()),
                    (b"x-ratelimit-reset", str(info["reset"]).encode()),
                ])
                message["headers"] = headers
            await send(message)
        
        await self.app(scope, receive, send_with_headers)

