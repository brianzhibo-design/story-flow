"""
通义万相 (Wanx) 图片生成供应商

官方文档: https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-wanxiang
"""
import asyncio
import httpx
import structlog
from typing import Optional, List

from app.config import settings
from app.ai_gateway.providers.base import BaseImageProvider

logger = structlog.get_logger()


class WanxProvider(BaseImageProvider):
    """通义万相图片生成供应商"""
    
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
        self.default_model = getattr(settings, 'WANX_MODEL', 'wanx-v1')
    
    async def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 576,
        n: int = 1,
        seed: int = None,
        style: str = None,
        **kwargs
    ) -> dict:
        """
        生成图片
        
        Args:
            prompt: 正向提示词
            negative_prompt: 负向提示词
            width: 宽度
            height: 高度
            n: 生成数量 (1-4)
            seed: 随机种子
            style: 风格预设
        
        Returns:
            {"image_url": "...", "task_id": "...", "seed": ...}
        """
        # 提交生成任务
        task_id = await self._submit_task(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            n=n,
            seed=seed,
            style=style
        )
        
        logger.info("wanx_task_submitted", task_id=task_id, prompt=prompt[:50])
        
        # 轮询结果
        result = await self._wait_for_result(task_id)
        
        return {
            "image_url": result["results"][0]["url"],
            "task_id": task_id,
            "seed": result.get("seed"),
            "all_images": [r["url"] for r in result["results"]]
        }
    
    async def _submit_task(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 576,
        n: int = 1,
        seed: int = None,
        style: str = None
    ) -> str:
        """提交生成任务"""
        
        # 尺寸映射 (通义万相支持的尺寸)
        size = self._map_size(width, height)
        
        payload = {
            "model": self.default_model,
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "size": size,
                "n": min(n, 4)
            }
        }
        
        if negative_prompt:
            payload["input"]["negative_prompt"] = negative_prompt
        
        if seed is not None:
            payload["parameters"]["seed"] = seed
        
        if style:
            payload["parameters"]["style"] = style
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"  # 异步模式
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/services/aigc/text2image/image-synthesis",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("output", {}).get("task_id"):
                return data["output"]["task_id"]
            
            raise Exception(f"万相 API 错误: {data}")
    
    async def _wait_for_result(self, task_id: str, timeout: int = 300) -> dict:
        """等待任务完成"""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        start_time = asyncio.get_event_loop().time()
        
        async with httpx.AsyncClient(timeout=30) as client:
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > timeout:
                    raise TimeoutError("万相生成超时")
                
                response = await client.get(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                status = data.get("output", {}).get("task_status")
                
                if status == "SUCCEEDED":
                    logger.info("wanx_task_completed", task_id=task_id)
                    return data["output"]
                elif status == "FAILED":
                    error_msg = data.get("output", {}).get("message", "未知错误")
                    raise Exception(f"万相生成失败: {error_msg}")
                
                logger.debug("wanx_task_pending", task_id=task_id, status=status)
                # 等待后重试
                await asyncio.sleep(2)
    
    def _map_size(self, width: int, height: int) -> str:
        """映射尺寸到万相支持的格式"""
        # 万相支持的尺寸
        sizes = {
            (1024, 1024): "1024*1024",
            (720, 1280): "720*1280",
            (1280, 720): "1280*720",
            (768, 1024): "768*1024",
            (1024, 768): "1024*768",
            (576, 1024): "576*1024",
            (1024, 576): "1024*576"
        }
        
        # 找最接近的尺寸
        best_size = "1024*576"  # 默认 16:9
        min_diff = float('inf')
        
        for (w, h), size_str in sizes.items():
            diff = abs(w - width) + abs(h - height)
            if diff < min_diff:
                min_diff = diff
                best_size = size_str
        
        return best_size
    
    async def check_health(self) -> bool:
        """健康检查"""
        try:
            # 简单测试 API 连通性
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.base_url}/tasks/test",
                    headers=headers
                )
                # 404 也说明 API 是通的
                return response.status_code in [200, 404]
        except Exception as e:
            logger.error("wanx_health_check_failed", error=str(e))
            return False


# 风格预设
WANX_STYLES = {
    "<auto>": "自动",
    "<3d cartoon>": "3D 卡通",
    "<anime>": "动漫",
    "<oil painting>": "油画",
    "<watercolor>": "水彩",
    "<sketch>": "素描",
    "<chinese painting>": "国画",
    "<flat illustration>": "扁平插画",
    "<photography>": "摄影",
    "<cyberpunk>": "赛博朋克"
}

