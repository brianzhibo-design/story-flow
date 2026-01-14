"""
分镜生成服务

使用 AI Gateway 生成分镜脚本
"""
import json
import structlog
from typing import Optional, List

from app.ai_gateway.router import get_ai_gateway

logger = structlog.get_logger()


class StoryboardService:
    """分镜生成服务"""
    
    def __init__(self):
        self.ai = get_ai_gateway()
    
    async def generate_storyboard(
        self,
        story_text: str,
        style: str = "电影",
        num_scenes: int = 10,
        aspect_ratio: str = "16:9"
    ) -> List[dict]:
        """
        生成分镜脚本
        
        Args:
            story_text: 故事文本
            style: 视觉风格 (电影/动漫/国画/3D等)
            num_scenes: 分镜数量
            aspect_ratio: 画面比例
        
        Returns:
            分镜列表，每个分镜包含:
            - scene_index: 分镜序号
            - text: 原文片段
            - scene_description: 场景描述
            - image_prompt: 中文图片提示词
            - image_prompt_en: 英文图片提示词
            - shot_type: 镜头类型
            - camera_movement: 运镜方式
            - duration: 建议时长
        """
        
        prompt = self._build_prompt(story_text, style, num_scenes, aspect_ratio)
        
        messages = [
            {
                "role": "system",
                "content": "你是一位专业的分镜师和视觉导演，擅长将故事文本转化为视觉分镜。请严格按照 JSON 格式输出。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            # 使用 JSON 模式获取结构化输出
            result = await self.ai.chat_json(messages, temperature=0.7)
            
            scenes = result.get("scenes", [])
            
            logger.info(
                "storyboard_generated",
                num_scenes=len(scenes),
                style=style
            )
            
            return scenes
            
        except Exception as e:
            logger.error("storyboard_generation_failed", error=str(e))
            raise
    
    def _build_prompt(
        self,
        story_text: str,
        style: str,
        num_scenes: int,
        aspect_ratio: str
    ) -> str:
        """构建分镜生成提示词"""
        
        return f"""请将以下故事文本转化为 {num_scenes} 个分镜画面。

## 故事文本
{story_text}

## 要求
1. 视觉风格：{style}
2. 画面比例：{aspect_ratio}
3. 分镜数量：约 {num_scenes} 个

## 输出格式
请输出 JSON 格式，结构如下：
```json
{{
  "scenes": [
    {{
      "scene_index": 1,
      "text": "对应的原文片段",
      "scene_description": "场景的详细视觉描述",
      "image_prompt": "用于图片生成的中文提示词，包含人物、场景、光影、构图等",
      "image_prompt_en": "English prompt for image generation, detailed and specific",
      "shot_type": "镜头类型：wide/medium/close-up/extreme-close-up",
      "camera_movement": "运镜方式：static/pan/tilt/zoom/dolly/crane",
      "duration": 5.0
    }}
  ]
}}
```

## 注意事项
1. image_prompt_en 必须是专业的英文提示词，包含：
   - 主体描述 (人物/物体)
   - 场景环境
   - 光影氛围
   - 镜头构图
   - 风格标签 (如 cinematic, {style} style)
2. 确保画面之间有视觉连贯性
3. 合理分配镜头类型，避免单一
4. duration 根据场景内容估算 (3-8秒)

请直接输出 JSON，不要包含其他文字。"""
    
    async def generate_scene_image(
        self,
        scene: dict,
        style: str = "电影"
    ) -> dict:
        """
        为单个分镜生成图片
        
        Args:
            scene: 分镜信息
            style: 视觉风格
        
        Returns:
            {"image_url": "...", "seed": ...}
        """
        prompt = scene.get("image_prompt_en", scene.get("image_prompt", ""))
        
        if not prompt:
            raise ValueError("分镜缺少提示词")
        
        # 添加风格后缀
        style_suffix = self._get_style_suffix(style)
        full_prompt = f"{prompt}, {style_suffix}"
        
        result = await self.ai.generate_image(
            prompt=full_prompt,
            negative_prompt="blurry, low quality, distorted, watermark, text",
            width=1024,
            height=576,
            seed=scene.get("seed")
        )
        
        logger.info(
            "scene_image_generated",
            scene_index=scene.get("scene_index"),
            image_url=result.get("image_url", "")[:50]
        )
        
        return result
    
    async def generate_scene_video(
        self,
        scene: dict,
        image_url: str
    ) -> dict:
        """
        为单个分镜生成视频
        
        Args:
            scene: 分镜信息
            image_url: 图片 URL
        
        Returns:
            {"video_url": "...", "duration": ...}
        """
        # 构建运镜提示词
        camera_movement = scene.get("camera_movement", "static")
        motion_prompt = self._get_motion_prompt(camera_movement)
        
        duration = scene.get("duration", 5.0)
        
        result = await self.ai.generate_video(
            image_url=image_url,
            prompt=motion_prompt,
            duration=min(duration, 10.0)  # 可灵最长 10 秒
        )
        
        logger.info(
            "scene_video_generated",
            scene_index=scene.get("scene_index"),
            video_url=result.get("video_url", "")[:50]
        )
        
        return result
    
    async def generate_scene_audio(
        self,
        scene: dict,
        voice: str = "zhixiaobai"
    ) -> dict:
        """
        为单个分镜生成配音
        
        Args:
            scene: 分镜信息
            voice: 音色
        
        Returns:
            {"audio_data": bytes, "duration": float}
        """
        text = scene.get("text", "")
        
        if not text:
            return {"audio_data": b"", "duration": 0}
        
        result = await self.ai.synthesize_speech(
            text=text,
            voice=voice
        )
        
        logger.info(
            "scene_audio_generated",
            scene_index=scene.get("scene_index"),
            duration=result.get("duration", 0)
        )
        
        return result
    
    def _get_style_suffix(self, style: str) -> str:
        """获取风格后缀"""
        style_map = {
            "电影": "cinematic, film grain, dramatic lighting",
            "动漫": "anime style, vibrant colors, cel shading",
            "国画": "chinese ink painting, watercolor, traditional art",
            "3D": "3D render, octane render, high quality",
            "写实": "photorealistic, 8k, ultra detailed",
            "油画": "oil painting, impressionist, brush strokes",
            "水彩": "watercolor, soft colors, artistic",
            "赛博朋克": "cyberpunk, neon lights, futuristic"
        }
        return style_map.get(style, "high quality, detailed")
    
    def _get_motion_prompt(self, camera_movement: str) -> str:
        """获取运镜提示词"""
        motion_map = {
            "static": "static shot, subtle movement",
            "pan": "camera panning slowly",
            "tilt": "camera tilting up/down",
            "zoom": "slow zoom in",
            "dolly": "camera moving forward",
            "crane": "crane shot, sweeping motion",
            "orbit": "camera orbiting around subject",
            "follow": "camera following the subject"
        }
        return motion_map.get(camera_movement, "subtle camera movement")


# 全局实例
_storyboard_service: StoryboardService = None


def get_storyboard_service() -> StoryboardService:
    """获取分镜服务实例"""
    global _storyboard_service
    if _storyboard_service is None:
        _storyboard_service = StoryboardService()
    return _storyboard_service

