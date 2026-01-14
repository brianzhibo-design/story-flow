"""
订阅与配额 API
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.subscription import PlanType, BillingCycle, UsageType
from app.services.subscription_service import SubscriptionService, QuotaService

router = APIRouter(prefix="/subscription", tags=["订阅"])


# ==================== 请求/响应模型 ====================

class PlanResponse(BaseModel):
    """计划响应"""
    type: str
    name: str
    price_monthly: float
    price_yearly: float
    projects_limit: int
    scenes_per_project: int
    storage_gb: float
    llm_tokens: int
    image_count: int
    video_count: int
    video_duration: int
    tts_chars: int
    can_export_hd: bool
    can_remove_watermark: bool
    can_use_premium_voices: bool
    can_collaborate: bool
    priority_queue: bool
    api_access: bool


class SubscriptionResponse(BaseModel):
    """订阅响应"""
    plan_type: str
    plan_name: str
    status: str
    billing_cycle: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    auto_renew: bool


class SubscribeRequest(BaseModel):
    """订阅请求"""
    plan_type: str = Field(..., description="计划类型: free/basic/pro/enterprise")
    billing_cycle: str = Field(default="monthly", description="计费周期: monthly/yearly")


class UsageSummaryResponse(BaseModel):
    """使用量摘要响应"""
    llm_tokens: dict
    image_gen: dict
    video_gen: dict
    video_duration: dict
    tts: dict
    storage: dict


# ==================== API 端点 ====================

@router.get("/plans")
async def get_plans(db=Depends(get_db)):
    """
    获取所有订阅计划
    """
    service = SubscriptionService(db)
    plans = await service.get_all_plans()
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "plans": [
                {
                    "type": p.type.value,
                    "name": p.name,
                    "description": p.description,
                    "price_monthly": p.price_monthly,
                    "price_yearly": p.price_yearly,
                    "projects_limit": p.projects_limit,
                    "scenes_per_project": p.scenes_per_project,
                    "storage_gb": p.storage_gb,
                    "llm_tokens": p.llm_tokens,
                    "image_count": p.image_count,
                    "video_count": p.video_count,
                    "video_duration": p.video_duration,
                    "tts_chars": p.tts_chars,
                    "can_export_hd": p.can_export_hd,
                    "can_remove_watermark": p.can_remove_watermark,
                    "can_use_premium_voices": p.can_use_premium_voices,
                    "can_collaborate": p.can_collaborate,
                    "priority_queue": p.priority_queue,
                    "api_access": p.api_access,
                }
                for p in plans
            ]
        }
    }


@router.get("/current")
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    获取当前用户订阅
    """
    try:
        service = SubscriptionService(db)
        subscription = await service.get_user_subscription(current_user.id)
        plan = await service.get_user_plan(current_user.id)
        
        # 确保 plan 不为 None
        if not plan:
            return {
                "code": 0,
                "message": "success",
                "data": None
            }
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "plan": {
                    "type": plan.type.value if hasattr(plan.type, 'value') else str(plan.type),
                    "name": plan.name,
                },
                "subscription": {
                    "status": subscription.status.value if subscription else "free",
                    "billing_cycle": subscription.billing_cycle.value if subscription else None,
                    "current_period_start": subscription.current_period_start if subscription else None,
                    "current_period_end": subscription.current_period_end if subscription else None,
                    "auto_renew": subscription.auto_renew if subscription else False,
                } if subscription else None,
                "limits": {
                    "projects": plan.projects_limit,
                    "scenes_per_project": plan.scenes_per_project,
                    "storage_gb": plan.storage_gb,
                    "llm_tokens": plan.llm_tokens,
                    "image_count": plan.image_count,
                    "video_count": plan.video_count,
                    "video_duration": plan.video_duration,
                    "tts_chars": plan.tts_chars,
                },
                "features": {
                    "can_export_hd": plan.can_export_hd,
                    "can_remove_watermark": plan.can_remove_watermark,
                    "can_use_premium_voices": plan.can_use_premium_voices,
                    "can_collaborate": plan.can_collaborate,
                    "priority_queue": plan.priority_queue,
                    "api_access": plan.api_access,
                }
            }
        }
    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.exception(f"Failed to get subscription: {e}")
        return {
            "code": 500,
            "message": str(e),
            "data": None
        }


@router.post("/subscribe")
async def subscribe(
    request: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    订阅计划
    
    注意：实际支付流程需要额外实现
    """
    try:
        plan_type = PlanType(request.plan_type)
        billing_cycle = BillingCycle(request.billing_cycle)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的参数: {e}")
    
    service = SubscriptionService(db)
    subscription = await service.subscribe(
        user_id=current_user.id,
        plan_type=plan_type,
        billing_cycle=billing_cycle
    )
    
    return {
        "code": 0,
        "message": "订阅成功",
        "data": {
            "subscription_id": str(subscription.id),
            "plan_type": plan_type.value,
            "billing_cycle": billing_cycle.value,
            "period_end": subscription.current_period_end.isoformat()
        }
    }


@router.post("/cancel")
async def cancel_subscription(
    reason: str = None,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    取消订阅
    """
    service = SubscriptionService(db)
    
    try:
        subscription = await service.cancel_subscription(
            user_id=current_user.id,
            reason=reason
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {
        "code": 0,
        "message": "订阅已取消，将在当前周期结束后失效",
        "data": {
            "cancelled_at": subscription.cancelled_at.isoformat(),
            "valid_until": subscription.current_period_end.isoformat()
        }
    }


@router.get("/usage")
async def get_usage_summary(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    获取使用量摘要
    """
    try:
        service = QuotaService(db)
        summary = await service.get_usage_summary(current_user.id)
        
        return {
            "code": 0,
            "message": "success",
            "data": summary
        }
    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.exception(f"Failed to get usage summary: {e}")
        return {
            "code": 500,
            "message": str(e),
            "data": None
        }


@router.get("/usage/history")
async def get_usage_history(
    usage_type: str = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    获取使用记录
    """
    service = QuotaService(db)
    
    usage_type_enum = None
    if usage_type:
        try:
            usage_type_enum = UsageType(usage_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的 usage_type: {usage_type}")
    
    records = await service.get_usage_history(
        user_id=current_user.id,
        usage_type=usage_type_enum,
        limit=limit
    )
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "records": [
                {
                    "id": str(r.id),
                    "type": r.usage_type.value,
                    "amount": r.amount,
                    "unit": r.unit,
                    "cost": r.cost,
                    "project_id": r.project_id,
                    "recorded_at": r.recorded_at.isoformat()
                }
                for r in records
            ]
        }
    }


@router.get("/check/{usage_type}")
async def check_quota(
    usage_type: str,
    amount: float = 1,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    检查配额
    """
    try:
        usage_type_enum = UsageType(usage_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的 usage_type: {usage_type}")
    
    service = QuotaService(db)
    quota = await service.check_quota(
        user_id=current_user.id,
        usage_type=usage_type_enum,
        amount=amount
    )
    
    return {
        "code": 0,
        "message": "success",
        "data": quota
    }

