"""
即梦 AI 供应商

图片生成和视频生成
API 文档: https://www.volcengine.com/docs/jimeng
"""

import httpx
import structlog

from app.config import settings
from app.ai_gateway.providers.base import BaseImageProvider, BaseVideoProvider
from app.core.exceptions import AIProviderError

logger = structlog.get_logger()


class JimengImageProvider(BaseImageProvider):
    """即梦图片生成"""
    
    def __init__(self):
        self.api_key = settings.JIMENG_API_KEY
        self.base_url = settings.JIMENG_BASE_URL
    
    async def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 576,
        **kwargs
    ) -> dict:
        """生成图片"""
        
        url = f"{self.base_url}/v2/images/generations"
        
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "num_images": 1,
            "guidance_scale": kwargs.get("cfg_scale", 7),
            "seed": kwargs.get("seed", -1),
        }
        
        # 如果指定了画风
        style = kwargs.get("style")
        if style:
            payload["style_preset"] = style
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                
                # 获取生成的图片
                image_data = data.get("data", [{}])[0]
                
                logger.info(
                    "jimeng_image_generated",
                    width=width,
                    height=height
                )
                
                return {
                    "image_url": image_data.get("url"),
                    "seed": image_data.get("seed"),
                }
                
        except httpx.HTTPStatusError as e:
            logger.error("jimeng_api_error", status=e.response.status_code)
            raise AIProviderError(f"Jimeng API error: {e.response.status_code}")
        except Exception as e:
            logger.exception("jimeng_error", error=str(e))
            raise AIProviderError(f"Jimeng error: {str(e)}")
    
    async def check_health(self) -> bool:
        """健康检查"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return response.status_code == 200
        except Exception:
            return False


class JimengVideoProvider(BaseVideoProvider):
    """即梦视频生成"""
    
    def __init__(self):
        self.api_key = settings.JIMENG_API_KEY
        self.base_url = settings.JIMENG_BASE_URL
    
    async def submit_task(
        self,
        image_url: str,
        prompt: str = "",
        duration: int = 5,
        **kwargs
    ) -> dict:
        """提交视频生成任务"""
        
        url = f"{self.base_url}/v2/videos/img2video"
        
        payload = {
            "image_url": image_url,
            "prompt": prompt,
            "duration": duration,
            "fps": kwargs.get("fps", 24),
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                
                return {
                    "task_id": data.get("task_id"),
                }
                
        except httpx.HTTPStatusError as e:
            logger.error("jimeng_video_submit_error", status=e.response.status_code)
            raise AIProviderError(f"Jimeng video submit error: {e.response.status_code}")
        except Exception as e:
            logger.exception("jimeng_video_error", error=str(e))
            raise AIProviderError(f"Jimeng video error: {str(e)}")
    
    async def get_task_status(self, task_id: str) -> dict:
        """获取任务状态"""
        
        url = f"{self.base_url}/v2/videos/task/{task_id}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                status = data.get("status", "")
                
                # 状态映射
                state_map = {
                    "pending": "pending",
                    "processing": "processing",
                    "success": "completed",
                    "failed": "failed",
                }
                
                return {
                    "state": state_map.get(status, "pending"),
                    "progress": data.get("progress", 0),
                    "video_url": data.get("video_url"),
                    "error": data.get("error_message"),
                }
                
        except Exception as e:
            logger.exception("jimeng_status_error", error=str(e))
            return {
                "state": "failed",
                "error": str(e),
            }
    
    async def check_health(self) -> bool:
        """健康检查"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return response.status_code == 200
        except Exception:
            return False
