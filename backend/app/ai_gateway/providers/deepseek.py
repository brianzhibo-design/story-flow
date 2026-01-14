"""
DeepSeek LLM 供应商

用于分镜脚本生成
"""

import httpx
import structlog

from app.config import settings
from app.ai_gateway.providers.base import BaseLLMProvider
from app.core.exceptions import AIProviderError

logger = structlog.get_logger()


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek LLM 供应商"""
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.default_model = "deepseek-chat"
    
    async def chat_completion(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: dict | None = None,
        **kwargs
    ) -> str:
        """调用 DeepSeek Chat API"""
        
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        
        if response_format:
            payload["response_format"] = response_format
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                logger.info(
                    "deepseek_completion",
                    model=model or self.default_model,
                    tokens=data.get("usage", {})
                )
                
                return content
                
        except httpx.HTTPStatusError as e:
            logger.error("deepseek_api_error", status=e.response.status_code, body=e.response.text)
            raise AIProviderError(f"DeepSeek API error: {e.response.status_code}")
        except Exception as e:
            logger.exception("deepseek_error", error=str(e))
            raise AIProviderError(f"DeepSeek error: {str(e)}")
    
    async def check_health(self) -> bool:
        """健康检查"""
        try:
            # 发送简单请求测试连通性
            await self.chat_completion(
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=5
            )
            return True
        except Exception:
            return False
