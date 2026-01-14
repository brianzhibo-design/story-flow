"""
支付 API

支持支付宝和微信支付
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payment", tags=["支付"])


# ==================== 请求模型 ====================

class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    plan_type: str = Field(..., description="计划类型: basic/pro/enterprise")
    billing_cycle: str = Field(default="monthly", description="计费周期: monthly/yearly")
    payment_method: str = Field(default="alipay", description="支付方式: alipay/wechat")


# ==================== API 端点 ====================

@router.post("/create-order")
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    创建支付订单
    
    Returns:
        {
            "order_no": "SF202412301234ABCD",
            "amount": 99,
            "pay_url": "https://..."
        }
    """
    service = PaymentService(db)
    
    try:
        result = await service.create_subscription_order(
            user_id=str(current_user.id),
            plan_type=request.plan_type,
            billing_cycle=request.billing_cycle,
            payment_method=request.payment_method
        )
        
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建订单失败: {str(e)}")


@router.get("/order/{order_no}")
async def query_order(
    order_no: str,
    db=Depends(get_db)
):
    """
    查询订单状态
    """
    service = PaymentService(db)
    
    try:
        result = await service.query_order(order_no)
        
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/notify/alipay")
async def alipay_notify(request: Request, db=Depends(get_db)):
    """
    支付宝异步回调
    
    支付宝会在用户支付成功后调用此接口
    需要返回 "success" 表示接收成功
    """
    # 获取表单数据
    form_data = await request.form()
    data = dict(form_data)
    
    service = PaymentService(db)
    
    success = await service.handle_alipay_notify(data)
    
    if success:
        return PlainTextResponse("success")
    else:
        return PlainTextResponse("fail")


@router.post("/notify/wechat")
async def wechat_notify(request: Request, db=Depends(get_db)):
    """
    微信支付异步回调
    
    微信会在用户支付成功后调用此接口
    需要返回 {"code": "SUCCESS"} 表示接收成功
    """
    # 获取 headers 和 body
    headers = dict(request.headers)
    body = await request.body()
    body_str = body.decode("utf-8")
    
    service = PaymentService(db)
    
    success = await service.handle_wechat_notify(headers, body_str)
    
    if success:
        return JSONResponse({"code": "SUCCESS", "message": ""})
    else:
        return JSONResponse(
            {"code": "FAIL", "message": "验证失败"},
            status_code=400
        )


@router.get("/price")
async def calculate_price(
    plan_type: str,
    billing_cycle: str = "monthly"
):
    """
    计算订阅价格
    
    Returns:
        {
            "original_price": 1188,
            "final_price": 990,
            "discount": 16.7,
            "saved": 198
        }
    """
    service = PaymentService(None)  # 不需要数据库
    
    try:
        result = service.calculate_price(plan_type, billing_cycle)
        
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/methods")
async def get_payment_methods():
    """
    获取可用支付方式
    """
    return {
        "code": 0,
        "message": "success",
        "data": {
            "methods": [
                {
                    "id": "alipay",
                    "name": "支付宝",
                    "icon": "alipay",
                    "description": "支持花呗、余额宝",
                    "enabled": True
                },
                {
                    "id": "wechat",
                    "name": "微信支付",
                    "icon": "wechat",
                    "description": "扫码支付",
                    "enabled": True
                }
            ]
        }
    }

