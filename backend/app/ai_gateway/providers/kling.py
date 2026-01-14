"""
可灵 (Kling) 视频生成供应商

官方文档: https://docs.qingque.cn/d/home/eZQBZRk0meMQvdm-4SdpkYNYd
支持两种认证方式:
1. API Key (Bearer Token) - 简单模式
2. AccessKey + SecretKey (签名) - 高级模式
"""
import time
import hmac
import hashlib
import base64
import asyncio
import httpx
import structlog
from typing import Optional

from app.config import settings
from app.ai_gateway.providers.base import BaseVideoProvider
from app.core.exceptions import AIProviderError

logger = structlog.get_logger()


class KlingProvider(BaseVideoProvider):
    """可灵视频生成供应商"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'KLING_API_KEY', None)
        self.access_key = getattr(settings, 'KLING_ACCESS_KEY', None)
        self.secret_key = getattr(settings, 'KLING_SECRET_KEY', None)
        self.base_url = getattr(settings, 'KLING_BASE_URL', 'https://api.klingai.com')
        
        # 确定认证方式
        self.use_signature = bool(self.access_key and self.secret_key)
    
    def _generate_signature(self, method: str, path: str, timestamp: int) -> str:
        """生成 API 签名"""
        if not self.secret_key:
            return ""
        string_to_sign = f"{method}\n{path}\n{timestamp}"
        signature = hmac.new(
            self.secret_key.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()
    
    def _get_headers(self, method: str = "POST", path: str = "") -> dict:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        
        if self.use_signature:
            timestamp = int(time.time())
            signature = self._generate_signature(method, path, timestamp)
            headers.update({
                "X-Access-Key": self.access_key,
                "X-Timestamp": str(timestamp),
                "X-Signature": signature
            })
        elif self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    async def generate(
        self,
        image_url: str,
        prompt: str = "",
        negative_prompt: str = "",
        duration: float = 5.0,
        mode: str = "std",  # std 或 pro
        cfg_scale: float = 0.5,
        **kwargs
    ) -> dict:
        """
        图生视频
        
        Args:
            image_url: 输入图片 URL
            prompt: 运动提示词
            negative_prompt: 负向提示词
            duration: 时长 (5 或 10 秒)
            mode: 模式 (std 标准 / pro 专业)
            cfg_scale: 提示词强度 (0-1)
        
        Returns:
            {"task_id": "...", "video_url": "..."}
        """
        path = "/v1/videos/image2video"
        
        payload = {
            "image": image_url,
            "duration": str(int(duration)),
            "mode": mode
        }
        
        if prompt:
            payload["prompt"] = prompt
            payload["cfg_scale"] = cfg_scale
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        headers = self._get_headers("POST", path)
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}{path}",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("code") == 0 or data.get("data", {}).get("task_id"):
                    task_id = data.get("data", {}).get("task_id")
                    
                    logger.info("kling_task_submitted", task_id=task_id)
                    
                    # 等待视频生成
                    result = await self._wait_for_result(task_id)
                    
                    return {
                        "task_id": task_id,
                        "video_url": result["video_url"],
                        "duration": duration
                    }
                else:
                    raise AIProviderError(f"可灵 API 错误: {data}")
        
        except httpx.HTTPStatusError as e:
            logger.error("kling_http_error", status=e.response.status_code, body=e.response.text[:200])
            raise AIProviderError(f"Kling HTTP 错误: {e.response.status_code}")
        except Exception as e:
            logger.exception("kling_error", error=str(e))
            raise AIProviderError(f"Kling 错误: {str(e)}")
    
    async def generate_text2video(
        self,
        prompt: str,
        negative_prompt: str = "",
        duration: float = 5.0,
        aspect_ratio: str = "16:9",
        mode: str = "std",
        **kwargs
    ) -> dict:
        """
        文生视频
        
        Args:
            prompt: 视频描述提示词
            negative_prompt: 负向提示词
            duration: 时长 (5 或 10 秒)
            aspect_ratio: 宽高比 (16:9, 9:16, 1:1)
            mode: 模式
        """
        path = "/v1/videos/text2video"
        
        payload = {
            "prompt": prompt,
            "duration": str(int(duration)),
            "aspect_ratio": aspect_ratio,
            "mode": mode
        }
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        headers = self._get_headers("POST", path)
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}{path}",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("code") == 0 or data.get("data", {}).get("task_id"):
                    task_id = data.get("data", {}).get("task_id")
                    result = await self._wait_for_result(task_id)
                    
                    return {
                        "task_id": task_id,
                        "video_url": result["video_url"],
                        "duration": duration
                    }
                else:
                    raise AIProviderError(f"可灵 API 错误: {data}")
        
        except Exception as e:
            logger.exception("kling_t2v_error", error=str(e))
            raise AIProviderError(f"Kling 文生视频错误: {str(e)}")
    
    async def query_task(self, task_id: str) -> dict:
        """查询任务状态"""
        path = f"/v1/videos/image2video/{task_id}"
        headers = self._get_headers("GET", path)
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}{path}",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            task_data = data.get("data", {})
            
            status = task_data.get("task_status", "")
            
            # 状态映射
            state_map = {
                "submitted": "pending",
                "processing": "processing",
                "succeed": "completed",
                "failed": "failed",
            }
            
            result = {
                "status": state_map.get(status, status),
                "video_url": None,
                "progress": 0
            }
            
            if status == "processing":
                result["progress"] = 50
            elif status == "succeed":
                result["progress"] = 100
                videos = task_data.get("task_result", {}).get("videos", [])
                if videos:
                    result["video_url"] = videos[0].get("url")
            
            return result
    
    async def _wait_for_result(self, task_id: str, timeout: int = 600) -> dict:
        """等待任务完成"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                raise TimeoutError("可灵视频生成超时")
            
            result = await self.query_task(task_id)
            
            if result["status"] == "completed":
                return result
            elif result["status"] == "failed":
                raise AIProviderError("可灵视频生成失败")
            
            logger.debug("kling_task_progress", task_id=task_id, progress=result.get("progress"))
            await asyncio.sleep(5)
    
    async def check_health(self) -> bool:
        """健康检查"""
        try:
            # 尝试查询一个不存在的任务
            path = "/v1/videos/image2video/test"
            headers = self._get_headers("GET", path)
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.base_url}{path}",
                    headers=headers
                )
                # 404 说明服务正常，只是任务不存在
                return response.status_code in [200, 404, 400]
        except Exception as e:
            logger.error("kling_health_check_failed", error=str(e))
            return False


# 兼容旧类名
KlingVideoProvider = KlingProvider
