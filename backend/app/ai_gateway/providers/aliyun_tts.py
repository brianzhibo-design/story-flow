"""
阿里云语音合成 (TTS) 供应商

官方文档: https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-speech-synthesis
"""
import asyncio
import base64
import httpx
import structlog
from typing import Optional, AsyncIterator, List

from app.config import settings
from app.ai_gateway.providers.tts_base import BaseTTSProvider

logger = structlog.get_logger()


class AliyunTTSProvider(BaseTTSProvider):
    """阿里云 TTS 供应商"""
    
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
    
    async def synthesize(
        self,
        text: str,
        voice: str = "zhixiaobai",  # 音色
        format: str = "mp3",
        sample_rate: int = 16000,
        volume: int = 50,
        speech_rate: int = 0,
        pitch_rate: int = 0,
        **kwargs
    ) -> dict:
        """
        语音合成
        
        Args:
            text: 待合成文本
            voice: 音色名称
            format: 输出格式 (mp3/wav/pcm)
            sample_rate: 采样率
            volume: 音量 (0-100)
            speech_rate: 语速 (-500 到 500)
            pitch_rate: 语调 (-500 到 500)
        
        Returns:
            {"audio_data": bytes, "duration": float}
        """
        payload = {
            "model": "sambert-zhichu-v1",  # 或其他模型
            "input": {
                "text": text
            },
            "parameters": {
                "voice": voice,
                "format": format,
                "sample_rate": sample_rate,
                "volume": volume,
                "rate": speech_rate / 100 if speech_rate else 1.0,  # 转换为倍率
                "pitch": pitch_rate / 100 if pitch_rate else 1.0
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/services/aigc/text2speech/synthesis",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("output", {}).get("audio"):
                audio_base64 = data["output"]["audio"]
                audio_data = base64.b64decode(audio_base64)
                
                # 估算时长 (按中文每秒 4 字计算)
                duration = len(text) / 4
                
                logger.info("aliyun_tts_synthesized", text_length=len(text), duration=duration)
                
                return {
                    "audio_data": audio_data,
                    "duration": duration,
                    "format": format
                }
            else:
                raise Exception(f"TTS 合成失败: {data}")
    
    async def synthesize_stream(
        self,
        text: str,
        voice: str = "zhixiaobai",
        **kwargs
    ) -> AsyncIterator[bytes]:
        """流式合成 (用于长文本)"""
        # 分段合成
        segments = self._split_text(text, max_length=300)
        
        for segment in segments:
            result = await self.synthesize(segment, voice=voice, **kwargs)
            yield result["audio_data"]
    
    def _split_text(self, text: str, max_length: int = 300) -> List[str]:
        """分割长文本"""
        segments = []
        current = ""
        
        for char in text:
            current += char
            if len(current) >= max_length and char in "。！？；\n":
                segments.append(current)
                current = ""
        
        if current:
            segments.append(current)
        
        return segments
    
    async def get_voices(self) -> List[dict]:
        """获取可用音色列表"""
        return ALIYUN_VOICES
    
    async def check_health(self) -> bool:
        """健康检查"""
        try:
            result = await self.synthesize("测试", voice="zhixiaobai")
            return len(result["audio_data"]) > 0
        except Exception as e:
            logger.error("aliyun_tts_health_check_failed", error=str(e))
            return False


# 可用音色列表
ALIYUN_VOICES = [
    # 中文女声
    {"id": "zhixiaobai", "name": "知小白", "gender": "female", "language": "zh", "style": "通用"},
    {"id": "zhixiaoxia", "name": "知小夏", "gender": "female", "language": "zh", "style": "温柔"},
    {"id": "zhixiaomei", "name": "知小妹", "gender": "female", "language": "zh", "style": "甜美"},
    {"id": "zhigui", "name": "知柜", "gender": "female", "language": "zh", "style": "客服"},
    {"id": "zhishuo", "name": "知硕", "gender": "female", "language": "zh", "style": "新闻"},
    {"id": "zhimi", "name": "知蜜", "gender": "female", "language": "zh", "style": "亲和"},
    {"id": "zhiyan", "name": "知颜", "gender": "female", "language": "zh", "style": "知性"},
    
    # 中文男声
    {"id": "zhichu", "name": "知厨", "gender": "male", "language": "zh", "style": "通用"},
    {"id": "zhide", "name": "知德", "gender": "male", "language": "zh", "style": "新闻"},
    {"id": "zhiyuan", "name": "知远", "gender": "male", "language": "zh", "style": "自然"},
    {"id": "zhiyue", "name": "知悦", "gender": "male", "language": "zh", "style": "温和"},
    {"id": "zhida", "name": "知达", "gender": "male", "language": "zh", "style": "磁性"},
    
    # 英文
    {"id": "stella", "name": "Stella", "gender": "female", "language": "en", "style": "通用"},
    {"id": "stanley", "name": "Stanley", "gender": "male", "language": "en", "style": "通用"},
    
    # 童声
    {"id": "zhitong", "name": "知童", "gender": "child", "language": "zh", "style": "童声"},
    {"id": "zhixiaoning", "name": "知小宁", "gender": "child", "language": "zh", "style": "活泼"},
]

