"""
通义千问 (Qwen) LLM 供应商

官方文档: https://help.aliyun.com/zh/dashscope/
"""
import json
import httpx
import structlog
from typing import Optional, AsyncIterator

from app.config import settings
from app.ai_gateway.providers.base import BaseLLMProvider

logger = structlog.get_logger()


class QwenProvider(BaseLLMProvider):
    """通义千问 LLM 供应商"""
    
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
        self.default_model = getattr(settings, 'QWEN_MODEL', 'qwen-plus')
    
    async def chat_completion(
        self,
        messages: list[dict],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: dict = None
    ) -> str:
        """
        聊天补全
        
        Args:
            messages: [{"role": "user", "content": "..."}]
            model: 模型名称
            temperature: 温度
            max_tokens: 最大 token
            response_format: {"type": "json_object"} 启用 JSON 模式
        """
        model = model or self.default_model
        
        # 构建请求
        payload = {
            "model": model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "result_format": "message"
            }
        }
        
        # JSON 模式
        if response_format and response_format.get("type") == "json_object":
            # 在系统提示中加入 JSON 要求
            if messages and messages[0]["role"] == "system":
                messages[0]["content"] += "\n\n请以 JSON 格式输出。"
            else:
                messages.insert(0, {
                    "role": "system",
                    "content": "请以 JSON 格式输出。"
                })
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.base_url}/services/aigc/text-generation/generation",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("output") and data["output"].get("choices"):
                return data["output"]["choices"][0]["message"]["content"]
            
            # 兼容另一种响应格式
            if data.get("output") and data["output"].get("text"):
                return data["output"]["text"]
            
            raise Exception(f"Qwen API 错误: {data}")
    
    async def chat_completion_stream(
        self,
        messages: list[dict],
        model: str = None,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """流式输出"""
        model = model or self.default_model
        
        payload = {
            "model": model,
            "input": {"messages": messages},
            "parameters": {
                "temperature": temperature,
                "result_format": "message",
                "incremental_output": True  # 增量输出
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-SSE": "enable"  # 启用 SSE
        }
        
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/services/aigc/text-generation/generation",
                json=payload,
                headers=headers
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        try:
                            data = json.loads(line[5:])
                            if data.get("output", {}).get("choices"):
                                content = data["output"]["choices"][0]["message"]["content"]
                                yield content
                        except json.JSONDecodeError:
                            continue
    
    async def chat_json(
        self,
        messages: list[dict],
        model: str = None,
        temperature: float = 0.3
    ) -> dict:
        """
        JSON 模式聊天 - 返回解析后的 JSON
        """
        response = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        
        # 尝试提取 JSON
        try:
            # 处理可能的 markdown 代码块
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
            logger.error("qwen_json_parse_failed", response=response[:200], error=str(e))
            raise ValueError(f"无法解析 JSON 响应: {e}")
    
    async def check_health(self) -> bool:
        """健康检查"""
        try:
            result = await self.chat_completion([
                {"role": "user", "content": "hello"}
            ], max_tokens=10)
            return bool(result)
        except Exception as e:
            logger.error("qwen_health_check_failed", error=str(e))
            return False


# 模型列表
QWEN_MODELS = {
    "qwen-max": "最强模型，适合复杂任务，¥0.02/千token",
    "qwen-plus": "平衡模型，性价比高，¥0.004/千token",
    "qwen-turbo": "快速模型，适合简单任务，¥0.002/千token",
    "qwen-long": "长文本模型，支持 1M token"
}

