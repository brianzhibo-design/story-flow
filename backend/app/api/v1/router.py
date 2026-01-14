# backend/app/api/v1/router.py
"""
API v1 路由聚合
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as projects_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.websocket import router as websocket_router
from app.api.v1.elements import router as elements_router
from app.api.v1.quota import router as quota_router
from app.api.v1.endpoints.enhance import router as enhance_router
from app.api.v1.endpoints.inpaint import router as inpaint_router
from app.api.v1.endpoints.controlnet import router as controlnet_router
from app.api.v1.endpoints.prompt import router as prompt_router
from app.api.v1.ai import router as ai_router
from app.api.v1.subscription import router as subscription_router
from app.api.v1.payment import router as payment_router
from app.api.v1.share import router as share_router

api_router = APIRouter()

# 认证相关
api_router.include_router(auth_router)

# 项目相关
api_router.include_router(projects_router)

# 任务相关
api_router.include_router(tasks_router)

# WebSocket
api_router.include_router(websocket_router)

# 视觉元素
api_router.include_router(elements_router)

# 配额管理
api_router.include_router(quota_router)

# 画质增强
api_router.include_router(enhance_router)

# 局部修改 (Inpainting)
api_router.include_router(inpaint_router)

# ControlNet
api_router.include_router(controlnet_router)

# 提示词融合
api_router.include_router(prompt_router)

# AI 服务
api_router.include_router(ai_router)

# 订阅与配额
api_router.include_router(subscription_router)

# 支付
api_router.include_router(payment_router)

# 分享协作
api_router.include_router(share_router)
