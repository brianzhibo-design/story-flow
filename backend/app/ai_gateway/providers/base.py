"""
AI 供应商基类

定义所有 AI 供应商的通用接口
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """LLM 供应商基类"""
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: dict | None = None,
        **kwargs
    ) -> str:
        """
        对话补全
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            model: 模型名称
            temperature: 温度
            max_tokens: 最大 token 数
            response_format: 响应格式 {"type": "json_object"}
            
        Returns:
            生成的文本
        """
        pass
    
    @abstractmethod
    async def check_health(self) -> bool:
        """健康检查"""
        pass


class BaseImageProvider(ABC):
    """图片生成供应商基类"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 576,
        **kwargs
    ) -> dict[str, Any]:
        """
        生成图片
        
        Args:
            prompt: 正向提示词
            negative_prompt: 负面提示词
            width: 宽度
            height: 高度
            
        Returns:
            {
                "image_url": "...",
                "image_data": bytes | None,
                "seed": int | None
            }
        """
        pass
    
    @abstractmethod
    async def check_health(self) -> bool:
        """健康检查"""
        pass


class BaseVideoProvider(ABC):
    """视频生成供应商基类"""
    
    @abstractmethod
    async def submit_task(
        self,
        image_url: str,
        prompt: str = "",
        duration: int = 5,
        **kwargs
    ) -> dict[str, Any]:
        """
        提交视频生成任务
        
        Args:
            image_url: 输入图片 URL
            prompt: 动作提示词
            duration: 时长（秒）
            
        Returns:
            {"task_id": "..."}
        """
        pass
    
    @abstractmethod
    async def get_task_status(self, task_id: str) -> dict[str, Any]:
        """
        获取任务状态
        
        Returns:
            {
                "state": "pending" | "processing" | "completed" | "failed",
                "progress": int,
                "video_url": str | None,
                "error": str | None
            }
        """
        pass
    
    @abstractmethod
    async def check_health(self) -> bool:
        """健康检查"""
        pass
