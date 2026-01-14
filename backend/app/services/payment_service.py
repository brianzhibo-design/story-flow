"""
支付服务

支持:
- 支付宝 (PC/H5 网页支付)
- 微信支付 (Native 扫码支付)
"""
import json
import time
import uuid
import base64
import hashlib
import hmac
import structlog
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode, quote_plus
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
import httpx

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.subscription import (
    PaymentOrder, UserSubscription, SubscriptionPlan,
    PlanType, BillingCycle, SubscriptionStatus, PaymentMethod,
    SUBSCRIPTION_PLANS_CONFIG
)

logger = structlog.get_logger()


class AlipayService:
    """支付宝支付服务"""
    
    def __init__(self):
        self.app_id = settings.ALIPAY_APP_ID
        self.private_key = settings.ALIPAY_PRIVATE_KEY
        self.public_key = settings.ALIPAY_PUBLIC_KEY
        self.gateway = settings.ALIPAY_GATEWAY
        self.notify_url = settings.ALIPAY_NOTIFY_URL
        self.return_url = settings.ALIPAY_RETURN_URL
    
    def create_order(
        self,
        order_no: str,
        amount: float,
        subject: str,
        body: str = ""
    ) -> str:
        """
        创建支付宝支付订单
        
        Returns:
            支付页面 URL
        """
        # 业务参数
        biz_content = {
            "out_trade_no": order_no,
            "total_amount": f"{amount:.2f}",
            "subject": subject,
            "body": body,
            "product_code": "FAST_INSTANT_TRADE_PAY"
        }
        
        # 公共参数
        params = {
            "app_id": self.app_id,
            "method": "alipay.trade.page.pay",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": self.notify_url,
            "return_url": self.return_url,
            "biz_content": json.dumps(biz_content, ensure_ascii=False)
        }
        
        # 签名
        params["sign"] = self._sign(params)
        
        # 构建 URL
        return f"{self.gateway}?{urlencode(params, quote_via=quote_plus)}"
    
    def verify_notify(self, data: dict) -> bool:
        """验证支付宝回调签名"""
        if not data:
            return False
        
        sign = data.pop("sign", None)
        sign_type = data.pop("sign_type", None)
        
        if not sign:
            return False
        
        # 构建待验签字符串
        unsigned_str = "&".join(
            f"{k}={data[k]}" 
            for k in sorted(data.keys()) 
            if data[k] and k not in ["sign", "sign_type"]
        )
        
        return self._verify(unsigned_str, sign)
    
    async def query_order(self, order_no: str) -> dict:
        """查询订单状态"""
        biz_content = {"out_trade_no": order_no}
        
        params = {
            "app_id": self.app_id,
            "method": "alipay.trade.query",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": json.dumps(biz_content)
        }
        
        params["sign"] = self._sign(params)
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(self.gateway, params=params)
            result = response.json()
            
            trade_response = result.get("alipay_trade_query_response", {})
            
            return {
                "trade_no": trade_response.get("trade_no"),
                "trade_status": trade_response.get("trade_status"),
                "buyer_id": trade_response.get("buyer_user_id"),
                "amount": trade_response.get("total_amount")
            }
    
    def _sign(self, params: dict) -> str:
        """RSA2 签名"""
        # 排序并拼接
        unsigned_str = "&".join(
            f"{k}={params[k]}" 
            for k in sorted(params.keys()) 
            if params[k]
        )
        
        # 签名
        key = RSA.import_key(self._format_private_key(self.private_key))
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new(unsigned_str.encode("utf-8"))
        sign = signer.sign(digest)
        
        return base64.b64encode(sign).decode("utf-8")
    
    def _verify(self, message: str, signature: str) -> bool:
        """验证签名"""
        try:
            key = RSA.import_key(self._format_public_key(self.public_key))
            verifier = PKCS1_v1_5.new(key)
            digest = SHA256.new(message.encode("utf-8"))
            
            return verifier.verify(digest, base64.b64decode(signature))
        except Exception as e:
            logger.error("alipay_verify_failed", error=str(e))
            return False
    
    def _format_private_key(self, key: str) -> str:
        """格式化私钥"""
        if "-----BEGIN" not in key:
            key = f"-----BEGIN RSA PRIVATE KEY-----\n{key}\n-----END RSA PRIVATE KEY-----"
        return key
    
    def _format_public_key(self, key: str) -> str:
        """格式化公钥"""
        if "-----BEGIN" not in key:
            key = f"-----BEGIN PUBLIC KEY-----\n{key}\n-----END PUBLIC KEY-----"
        return key


class WechatPayService:
    """微信支付 V3 API"""
    
    def __init__(self):
        self.app_id = settings.WECHAT_APP_ID
        self.mch_id = settings.WECHAT_MCH_ID
        self.api_v3_key = settings.WECHAT_API_V3_KEY
        self.private_key = settings.WECHAT_PRIVATE_KEY
        self.cert_serial_no = settings.WECHAT_CERT_SERIAL_NO
        self.notify_url = settings.WECHAT_NOTIFY_URL
        self.base_url = "https://api.mch.weixin.qq.com"
    
    async def create_native_order(
        self,
        order_no: str,
        amount: float,
        description: str
    ) -> str:
        """
        创建 Native 扫码支付订单
        
        Returns:
            微信支付二维码链接 (code_url)
        """
        url = "/v3/pay/transactions/native"
        
        data = {
            "appid": self.app_id,
            "mchid": self.mch_id,
            "description": description,
            "out_trade_no": order_no,
            "notify_url": self.notify_url,
            "amount": {
                "total": int(amount * 100),  # 分
                "currency": "CNY"
            }
        }
        
        headers = self._build_auth_header("POST", url, json.dumps(data))
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}{url}",
                json=data,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error("wechat_create_order_failed", 
                           status=response.status_code, 
                           body=response.text)
                raise Exception(f"微信支付创建订单失败: {response.text}")
            
            result = response.json()
            return result["code_url"]
    
    def verify_notify(self, headers: dict, body: str) -> dict:
        """
        验证微信支付回调并解密数据
        
        Returns:
            解密后的通知数据
        """
        # 验证签名
        timestamp = headers.get("Wechatpay-Timestamp")
        nonce = headers.get("Wechatpay-Nonce")
        signature = headers.get("Wechatpay-Signature")
        
        message = f"{timestamp}\n{nonce}\n{body}\n"
        
        # TODO: 验证签名 (需要下载微信平台证书)
        # 这里简化处理，实际生产环境需要完整验证
        
        # 解密数据
        data = json.loads(body)
        resource = data.get("resource", {})
        
        ciphertext = resource.get("ciphertext")
        nonce = resource.get("nonce")
        associated_data = resource.get("associated_data", "")
        
        decrypted = self._decrypt_aes_gcm(ciphertext, nonce, associated_data)
        
        return json.loads(decrypted)
    
    async def query_order(self, order_no: str) -> dict:
        """查询订单状态"""
        url = f"/v3/pay/transactions/out-trade-no/{order_no}"
        params = {"mchid": self.mch_id}
        
        headers = self._build_auth_header("GET", f"{url}?mchid={self.mch_id}", "")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}{url}",
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                return {"trade_state": "NOTPAY"}
            
            result = response.json()
            return {
                "trade_no": result.get("transaction_id"),
                "trade_state": result.get("trade_state"),
                "payer_openid": result.get("payer", {}).get("openid"),
                "amount": result.get("amount", {}).get("total", 0) / 100
            }
    
    def _build_auth_header(self, method: str, url: str, body: str) -> dict:
        """构建认证头"""
        timestamp = str(int(time.time()))
        nonce = uuid.uuid4().hex
        
        # 签名字符串
        message = f"{method}\n{url}\n{timestamp}\n{nonce}\n{body}\n"
        
        # 签名
        signature = self._sign(message)
        
        authorization = (
            f'WECHATPAY2-SHA256-RSA2048 '
            f'mchid="{self.mch_id}",'
            f'nonce_str="{nonce}",'
            f'signature="{signature}",'
            f'timestamp="{timestamp}",'
            f'serial_no="{self.cert_serial_no}"'
        )
        
        return {
            "Authorization": authorization,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _sign(self, message: str) -> str:
        """RSA 签名"""
        key = RSA.import_key(self._format_private_key(self.private_key))
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new(message.encode("utf-8"))
        sign = signer.sign(digest)
        return base64.b64encode(sign).decode("utf-8")
    
    def _decrypt_aes_gcm(self, ciphertext: str, nonce: str, associated_data: str) -> str:
        """AES-GCM 解密"""
        key = self.api_v3_key.encode("utf-8")
        nonce_bytes = nonce.encode("utf-8")
        ciphertext_bytes = base64.b64decode(ciphertext)
        associated_data_bytes = associated_data.encode("utf-8")
        
        # 分离密文和 tag
        tag = ciphertext_bytes[-16:]
        ciphertext_bytes = ciphertext_bytes[:-16]
        
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce_bytes)
        cipher.update(associated_data_bytes)
        
        return cipher.decrypt_and_verify(ciphertext_bytes, tag).decode("utf-8")
    
    def _format_private_key(self, key: str) -> str:
        """格式化私钥"""
        if key and "-----BEGIN" not in key:
            key = f"-----BEGIN RSA PRIVATE KEY-----\n{key}\n-----END RSA PRIVATE KEY-----"
        return key or ""


class PaymentService:
    """统一支付服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.alipay = AlipayService()
        self.wechat = WechatPayService()
    
    async def create_subscription_order(
        self,
        user_id: str,
        plan_type: str,
        billing_cycle: str = "monthly",
        payment_method: str = "alipay"
    ) -> dict:
        """
        创建订阅支付订单
        
        Args:
            user_id: 用户 ID
            plan_type: 计划类型 (basic/pro/enterprise)
            billing_cycle: 计费周期 (monthly/yearly)
            payment_method: 支付方式 (alipay/wechat)
        
        Returns:
            {
                "order_no": "xxx",
                "amount": 99,
                "pay_url": "https://..."
            }
        """
        # 验证计划
        try:
            plan_enum = PlanType(plan_type)
            cycle_enum = BillingCycle(billing_cycle)
            method_enum = PaymentMethod(payment_method)
        except ValueError as e:
            raise ValueError(f"无效的参数: {e}")
        
        if plan_enum == PlanType.FREE:
            raise ValueError("免费计划无需支付")
        
        # 计算价格
        price_info = self.calculate_price(plan_type, billing_cycle)
        amount = price_info["final_price"]
        
        # 生成订单号
        order_no = f"SF{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
        
        # 创建订单记录
        order = PaymentOrder(
            user_id=user_id,
            order_no=order_no,
            plan_type=plan_enum,
            billing_cycle=cycle_enum,
            amount=amount,
            payment_method=method_enum,
            payment_status="pending"
        )
        self.db.add(order)
        await self.db.commit()
        
        # 创建支付
        subject = f"StoryFlow {SUBSCRIPTION_PLANS_CONFIG[plan_enum]['name']} 订阅"
        
        if payment_method == "alipay":
            pay_url = self.alipay.create_order(order_no, amount, subject)
        else:
            pay_url = await self.wechat.create_native_order(order_no, amount, subject)
        
        logger.info(
            "payment_order_created",
            order_no=order_no,
            user_id=user_id,
            amount=amount,
            method=payment_method
        )
        
        return {
            "order_no": order_no,
            "amount": amount,
            "pay_url": pay_url,
            "plan_type": plan_type,
            "billing_cycle": billing_cycle
        }
    
    async def handle_alipay_notify(self, data: dict) -> bool:
        """处理支付宝异步回调"""
        # 验证签名
        if not self.alipay.verify_notify(data.copy()):
            logger.warning("alipay_notify_verify_failed", data=data)
            return False
        
        order_no = data.get("out_trade_no")
        trade_status = data.get("trade_status")
        trade_no = data.get("trade_no")
        
        # 只处理成功状态
        if trade_status not in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
            return True  # 非成功状态也返回成功，避免重复通知
        
        # 激活订阅
        await self._activate_subscription(order_no, trade_no)
        
        return True
    
    async def handle_wechat_notify(self, headers: dict, body: str) -> bool:
        """处理微信支付异步回调"""
        try:
            data = self.wechat.verify_notify(headers, body)
        except Exception as e:
            logger.error("wechat_notify_verify_failed", error=str(e))
            return False
        
        order_no = data.get("out_trade_no")
        trade_state = data.get("trade_state")
        trade_no = data.get("transaction_id")
        
        if trade_state != "SUCCESS":
            return True
        
        # 激活订阅
        await self._activate_subscription(order_no, trade_no)
        
        return True
    
    async def query_order(self, order_no: str) -> dict:
        """查询订单状态"""
        # 查数据库
        stmt = select(PaymentOrder).where(PaymentOrder.order_no == order_no)
        result = await self.db.execute(stmt)
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError("订单不存在")
        
        return {
            "order_no": order.order_no,
            "plan_type": order.plan_type.value,
            "amount": order.amount,
            "payment_status": order.payment_status,
            "paid_at": order.paid_at.isoformat() if order.paid_at else None
        }
    
    async def _activate_subscription(self, order_no: str, trade_no: str):
        """激活订阅"""
        # 查询订单
        stmt = select(PaymentOrder).where(PaymentOrder.order_no == order_no)
        result = await self.db.execute(stmt)
        order = result.scalar_one_or_none()
        
        if not order:
            logger.error("order_not_found", order_no=order_no)
            return
        
        if order.payment_status == "paid":
            logger.info("order_already_paid", order_no=order_no)
            return
        
        # 更新订单状态
        order.payment_status = "paid"
        order.external_order_id = trade_no
        order.paid_at = datetime.utcnow()
        
        # 获取计划
        stmt = select(SubscriptionPlan).where(SubscriptionPlan.type == order.plan_type)
        result = await self.db.execute(stmt)
        plan = result.scalar_one_or_none()
        
        if not plan:
            # 如果计划不存在，创建默认计划
            plan_config = SUBSCRIPTION_PLANS_CONFIG.get(order.plan_type, {})
            plan = SubscriptionPlan(type=order.plan_type, **plan_config)
            self.db.add(plan)
        
        # 计算订阅周期
        if order.billing_cycle == BillingCycle.YEARLY:
            period_end = datetime.utcnow() + timedelta(days=365)
        else:
            period_end = datetime.utcnow() + timedelta(days=30)
        
        # 查询现有订阅
        stmt = select(UserSubscription).where(
            UserSubscription.user_id == order.user_id,
            UserSubscription.status == SubscriptionStatus.ACTIVE
        )
        result = await self.db.execute(stmt)
        existing_sub = result.scalar_one_or_none()
        
        if existing_sub:
            # 升级现有订阅
            existing_sub.plan_id = plan.id
            existing_sub.billing_cycle = order.billing_cycle
            existing_sub.current_period_start = datetime.utcnow()
            existing_sub.current_period_end = period_end
            existing_sub.payment_method = order.payment_method
            existing_sub.last_payment_at = datetime.utcnow()
        else:
            # 创建新订阅
            subscription = UserSubscription(
                user_id=order.user_id,
                plan_id=plan.id,
                status=SubscriptionStatus.ACTIVE,
                billing_cycle=order.billing_cycle,
                current_period_start=datetime.utcnow(),
                current_period_end=period_end,
                payment_method=order.payment_method,
                last_payment_at=datetime.utcnow()
            )
            self.db.add(subscription)
        
        await self.db.commit()
        
        logger.info(
            "subscription_activated",
            order_no=order_no,
            user_id=order.user_id,
            plan_type=order.plan_type.value
        )
    
    def calculate_price(self, plan_type: str, billing_cycle: str = "monthly") -> dict:
        """
        计算订阅价格
        
        Returns:
            {
                "original_price": 99,
                "final_price": 99,
                "discount": 0,
                "saved": 0
            }
        """
        try:
            plan_enum = PlanType(plan_type)
        except ValueError:
            raise ValueError(f"无效的计划类型: {plan_type}")
        
        config = SUBSCRIPTION_PLANS_CONFIG.get(plan_enum)
        if not config:
            raise ValueError(f"计划 {plan_type} 不存在")
        
        if billing_cycle == "yearly":
            monthly = config["price_monthly"]
            yearly = config["price_yearly"]
            original = monthly * 12
            
            return {
                "original_price": original,
                "final_price": yearly,
                "discount": round((1 - yearly / original) * 100, 1) if original > 0 else 0,
                "saved": original - yearly
            }
        else:
            price = config["price_monthly"]
            return {
                "original_price": price,
                "final_price": price,
                "discount": 0,
                "saved": 0
            }

