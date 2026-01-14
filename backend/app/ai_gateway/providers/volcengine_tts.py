"""
火山引擎 TTS

API: https://www.volcengine.com/docs/6561
"""

import base64
import httpx
import structlog

from app.config import settings
from app.ai_gateway.providers.tts_base import BaseTTSProvider

logger = structlog.get_logger()


class VolcengineTTSProvider(BaseTTSProvider):
    """火山引擎 TTS"""
    
    def __init__(self):
        self.app_id = settings.VOLCENGINE_TTS_APP_ID or ""
        self.access_token = settings.VOLCENGINE_TTS_TOKEN or ""
        self.base_url = "https://openspeech.bytedance.com/api/v1/tts"
    
    async def synthesize(
        self,
        text: str,
        voice_id: str = "zh_female_qingxin",
        speed: float = 1.0,
        pitch: float = 1.0,
        **kwargs
    ) -> dict:
        """合成语音"""
        
        payload = {
            "app": {"appid": self.app_id, "token": self.access_token, "cluster": "volcano_tts"},
            "user": {"uid": "storyflow"},
            "audio": {
                "voice_type": voice_id,
                "encoding": "mp3",
                "speed_ratio": speed,
                "pitch_ratio": pitch
            },
            "request": {"reqid": f"sf_{hash(text)}", "text": text, "operation": "query"}
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                self.base_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") != 3000:
                raise Exception(f"TTS error: {data.get('message')}")
            
            # 解码音频
            audio_base64 = data["data"]
            audio_bytes = base64.b64decode(audio_base64)
            
            # 计算时长（粗略估计）
            duration = len(text) * 0.3 / speed
            
            return {
                "audio_data": audio_bytes,
                "duration": duration,
                "format": "mp3"
            }
    
    async def get_voices(self) -> list[dict]:
        """获取可用音色"""
        return [
            {"id": "zh_female_qingxin", "name": "清新女声", "gender": "female", "language": "zh"},
            {"id": "zh_male_chunhou", "name": "醇厚男声", "gender": "male", "language": "zh"},
            {"id": "zh_female_sichuan", "name": "四川女声", "gender": "female", "language": "zh"},
            {"id": "zh_male_jingqiang", "name": "京腔男声", "gender": "male", "language": "zh"},
            {"id": "en_female_sarah", "name": "Sarah", "gender": "female", "language": "en"},
            {"id": "en_male_adam", "name": "Adam", "gender": "male", "language": "en"},
        ]
    
    async def check_health(self) -> bool:
        """健康检查"""
        if not self.app_id or not self.access_token:
            return False
        try:
            await self.synthesize("测试", voice_id="zh_female_qingxin")
            return True
        except Exception:
            return False

