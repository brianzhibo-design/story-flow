"""TTS 供应商基类"""

from abc import ABC, abstractmethod


class BaseTTSProvider(ABC):
    """TTS 供应商基类"""
    
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice_id: str = "default",
        speed: float = 1.0,
        pitch: float = 1.0,
        **kwargs
    ) -> dict:
        """
        合成语音
        
        Returns:
            {"audio_data": bytes, "duration": float, "format": "mp3"}
        """
        pass
    
    @abstractmethod
    async def get_voices(self) -> list[dict]:
        """获取可用音色列表"""
        pass
    
    @abstractmethod
    async def check_health(self) -> bool:
        """健康检查"""
        pass

