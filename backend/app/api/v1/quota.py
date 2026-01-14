"""
配额管理 API
"""

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_db
from app.models.user import User, PlanType
from app.services.quota_service import QuotaService, PLAN_QUOTAS
from app.schemas.base import ResponseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/quota", tags=["Quota"])


@router.get("/status")
async def get_quota_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """获取当前用户的配额状态"""
    try:
        service = QuotaService(db)
        status = await service.get_quota_status(current_user.id)
        
        return ResponseModel(code=0, message="success", data=status)
    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.exception(f"Failed to get quota status: {e}")
        return ResponseModel(code=500, message=str(e), data=None)


@router.get("/plans")
async def get_available_plans() -> ResponseModel:
    """获取可用的套餐方案"""
    plans = []
    for plan_type, config in PLAN_QUOTAS.items():
        plans.append({
            "id": plan_type.value,
            "name": {
                "free": "免费版",
                "premium": "专业版",
                "enterprise": "企业版"
            }.get(plan_type.value, plan_type.value),
            "limits": config,
            "price": {
                "free": 0,
                "premium": 99,
                "enterprise": 499
            }.get(plan_type.value, 0)
        })
    
    return ResponseModel(code=0, message="success", data=plans)


@router.post("/upgrade/{plan_id}")
async def upgrade_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """
    升级套餐
    
    注意：实际场景需要对接支付系统
    """
    try:
        new_plan = PlanType(plan_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的套餐类型")
    
    service = QuotaService(db)
    quota = await service.upgrade_plan(current_user.id, new_plan)
    
    return ResponseModel(
        code=0,
        message="套餐升级成功",
        data={
            "plan": quota.plan_type.value,
            "total_credits": quota.total_credits,
            "reset_at": quota.reset_at.isoformat() if quota.reset_at else None
        }
    )


@router.post("/reset")
async def reset_quota(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """
    重置配额（管理员功能）
    """
    # 检查是否是管理员
    from app.models.user import UserRole
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    service = QuotaService(db)
    await service.reset_monthly_quota(current_user.id)
    
    return ResponseModel(code=0, message="配额已重置", data=None)

