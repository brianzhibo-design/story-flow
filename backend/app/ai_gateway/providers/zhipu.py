"""
智谱 GLM-4 LLM 供应商

官方文档: https://open.bigmodel.cn/dev/api
"""
import jwt
import time
import httpx
import json
import structlog
from typing import Optional, AsyncIterator

from app.config import settings
from app.ai_gateway.providers.base import BaseLLMProvider

logger = structlog.get_logger()


class ZhipuProvider(BaseLLMProvider):
    """智谱 GLM-4 LLM 供应商"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'ZHIPU_API_KEY', None)
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"
        self.default_model = "glm-4"
    
    def _generate_token(self, exp_seconds: int = 3600) -> str:
        """生成 JWT Token"""
        if not self.api_key:
            raise ValueError("ZHIPU_API_KEY 未配置")
        
        try:
            api_key_parts = self.api_key.split(".")
            api_key_id = api_key_parts[0]
            api_secret = api_key_parts[1]
        except IndexError:
            raise ValueError("ZHIPU_API_KEY 格式错误，应为 'id.secret'")
        
        payload = {
            "api_key": api_key_id,
            "exp": int(time.time()) + exp_seconds,
            "timestamp": int(time.time() * 1000)
        }
        
        return jwt.encode(payload, api_secret, algorithm="HS256")
    
    async def chat_completion(
        self,
        messages: list[dict],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: dict = None,
        **kwargs
    ) -> str:
        """
        聊天补全
        
        Args:
            messages: 消息列表
            model: 模型名称 (glm-4, glm-4-plus, glm-4v, glm-4-long)
            temperature: 温度
            max_tokens: 最大 token
            response_format: 响应格式
        """
        model = model or self.default_model
        
        headers = {
            "Authorization": f"Bearer {self._generate_token()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # JSON 模式
        if response_format and response_format.get("type") == "json_object":
            # 在系统提示中加入 JSON 要求
            if messages and messages[0]["role"] == "system":
                messages[0]["content"] += "\n\n请以有效的 JSON 格式输出。"
            else:
                messages.insert(0, {
                    "role": "system",
                    "content": "请以有效的 JSON 格式输出。"
                })
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"]
            
            raise Exception(f"智谱 API 错误: {data}")
    
    async def chat_completion_stream(
        self,
        messages: list[dict],
        model: str = None,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """流式输出"""
        model = model or self.default_model
        
        headers = {
            "Authorization": f"Bearer {self._generate_token()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
    
    async def chat_json(
        self,
        messages: list[dict],
        model: str = None,
        temperature: float = 0.3
    ) -> dict:
        """JSON 模式聊天"""
        response = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        
        # 尝试提取 JSON
        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error("zhipu_json_parse_failed", response=response[:200], error=str(e))
            raise ValueError(f"无法解析 JSON 响应: {e}")
    
    async def check_health(self) -> bool:
        """健康检查"""
        if not self.api_key:
            return False
        
        try:
            result = await self.chat_completion(
                [{"role": "user", "content": "hi"}],
                max_tokens=5
            )
            return bool(result)
        except Exception as e:
            logger.error("zhipu_health_check_failed", error=str(e))
            return False


# 模型列表
ZHIPU_MODELS = {
    "glm-4": {
        "name": "GLM-4",
        "description": "最新一代基座模型",
        "price_per_1k_tokens": 0.1,
        "max_tokens": 128000
    },
    "glm-4-plus": {
        "name": "GLM-4 Plus",
        "description": "增强版，更强推理能力",
        "price_per_1k_tokens": 0.05,
        "max_tokens": 128000
    },
    "glm-4v": {
        "name": "GLM-4V",
        "description": "多模态模型，支持图片理解",
        "price_per_1k_tokens": 0.1,
        "max_tokens": 8192
    },
    "glm-4-long": {
        "name": "GLM-4 Long",
        "description": "超长上下文，支持 1M token",
        "price_per_1k_tokens": 0.001,
        "max_tokens": 1000000
    },
    "glm-4-flash": {
        "name": "GLM-4 Flash",
        "description": "快速推理，低成本",
        "price_per_1k_tokens": 0.0001,
        "max_tokens": 128000
    }
}

