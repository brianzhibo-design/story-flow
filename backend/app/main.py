# backend/app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.v1.router import api_router
from app.core.database import init_db, close_db
from app.core.redis import redis_client
from app.core.storage import storage_client
from app.core.exceptions import StoryFlowException
from app.schemas.base import error_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    # 初始化数据库（创建表）
    await init_db()
    print("📦 Database initialized")
    
    # 初始化订阅计划数据
    try:
        from app.core.database import async_session_maker
        from app.services.subscription_service import SubscriptionService
        
        async with async_session_maker() as db:
            subscription_service = SubscriptionService(db)
            await subscription_service.init_plans()
            print("💎 Subscription plans initialized")
    except Exception as e:
        print(f"⚠️ Failed to initialize subscription plans: {e}")
    
    # 连接 Redis（忽略连接失败，本地开发可以没有 Redis）
    try:
        await redis_client.connect()
        print("🔗 Redis connected")
    except Exception as e:
        print(f"⚠️ Redis connection failed (will use fallback): {e}")
    
    # 初始化存储（忽略失败，本地开发可以没有 MinIO）
    try:
        storage_client.ensure_bucket()
        print("📁 Storage initialized")
    except Exception as e:
        print(f"⚠️ Storage initialization failed (will use fallback): {e}")
    
    print("🚀 StoryFlow API started")
    
    yield
    
    # 关闭时
    try:
        await redis_client.disconnect()
    except Exception:
        pass
    await close_db()
    print("👋 StoryFlow API shutdown")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI视频创作平台API",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    
    # 全局异常处理
    @app.exception_handler(StoryFlowException)
    async def storyflow_exception_handler(
        request: Request,
        exc: StoryFlowException
    ):
        # 根据异常类型确定 HTTP 状态码
        if exc.code < 1000:
            # 标准 HTTP 错误码
            http_status = exc.code
        elif 1001 <= exc.code <= 1010:
            # 认证相关错误 (1001-1010) 返回 401
            http_status = 401
        else:
            # 其他业务错误返回 400
            http_status = 400
        
        return JSONResponse(
            status_code=http_status,
            content=error_response(exc.code, exc.message, exc.details),
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=error_response(500, "Internal Server Error"),
        )
    
    # 健康检查
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    @app.get("/ready")
    async def ready_check():
        # 可以添加数据库、Redis连接检查
        return {"status": "ready"}
    
    return app


app = create_app()
