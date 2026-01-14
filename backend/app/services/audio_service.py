"""
配音服务

处理分镜配音生成
"""

from io import BytesIO
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scene import Scene
from app.services.file_service import get_file_service
from app.ai_gateway.providers.volcengine_tts import VolcengineTTSProvider


class AudioService:
    """配音服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_service = get_file_service()
        self.tts = VolcengineTTSProvider()
    
    async def generate_scene_audio(
        self,
        scene: Scene,
        project_id: str,
        voice_config: dict = None
    ) -> dict:
        """
        生成分镜配音
        
        voice_config: {
            "default_voice": "zh_female_qingxin",
            "character_voices": {"李明": "zh_male_chunhou", "小红": "zh_female_qingxin"},
            "speed": 1.0
        }
        """
        config = voice_config or {}
        default_voice = config.get("default_voice", "zh_female_qingxin")
        char_voices = config.get("character_voices", {})
        speed = config.get("speed", 1.0)
        
        text = scene.text
        if not text:
            return {"error": "No text for audio"}
        
        # 检测是否有角色对话（简单判断）
        voice_id = default_voice
        
        # 如果场景只有一个角色，使用该角色的音色
        if scene.characters and len(scene.characters) == 1:
            char_name = scene.characters[0]
            voice_id = char_voices.get(char_name, default_voice)
        
        # 合成
        result = await self.tts.synthesize(
            text=text,
            voice_id=voice_id,
            speed=speed
        )
        
        # 保存
        audio_data = BytesIO(result["audio_data"])
        saved = await self.file_service.save_scene_audio(
            project_id=project_id,
            scene_id=str(scene.id),
            data=audio_data
        )
        
        return {
            "audio_url": saved.url,
            "duration": result["duration"]
        }
    
    async def get_available_voices(self) -> list[dict]:
        """获取可用音色"""
        return await self.tts.get_voices()

