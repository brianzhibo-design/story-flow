"""
Mock AI 供应商 - 用于开发测试

当 AI_MOCK_MODE=true 时使用，无需真实 API Key
"""
import asyncio
import json
import random
import structlog
from typing import Optional, List, AsyncIterator

from app.ai_gateway.providers.base import BaseLLMProvider, BaseImageProvider, BaseVideoProvider
from app.ai_gateway.providers.tts_base import BaseTTSProvider

logger = structlog.get_logger()


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM 供应商"""
    
    async def chat_completion(
        self,
        messages: list[dict],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: dict = None
    ) -> str:
        """模拟聊天响应"""
        await asyncio.sleep(0.5)  # 模拟延迟
        
        user_message = messages[-1]["content"] if messages else ""
        
        # 检测是否需要 JSON 响应
        if response_format and response_format.get("type") == "json_object":
            return json.dumps({
                "response": "这是一个模拟的 JSON 响应",
                "model": model or "mock-model",
                "message": user_message[:50]
            }, ensure_ascii=False)
        
        # 检测分镜生成请求
        if "分镜" in user_message or "scene" in user_message.lower():
            return self._generate_mock_storyboard()
        
        return f"[Mock] 收到消息: {user_message[:100]}..."
    
    async def chat_completion_stream(
        self,
        messages: list[dict],
        model: str = None,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """模拟流式响应"""
        response = await self.chat_completion(messages, model, temperature)
        for char in response:
            await asyncio.sleep(0.01)
            yield char
    
    async def chat_json(
        self,
        messages: list[dict],
        model: str = None,
        temperature: float = 0.3
    ) -> dict:
        """模拟 JSON 响应"""
        response = await self.chat_completion(
            messages, model, temperature,
            response_format={"type": "json_object"}
        )
        return json.loads(response)
    
    def _generate_mock_storyboard(self) -> str:
        """生成模拟分镜数据"""
        scenes = [
            {
                "scene_index": i,
                "text": f"这是第 {i} 个分镜的文本内容",
                "scene_description": f"场景 {i} 的详细描述",
                "image_prompt_en": f"Scene {i}: A beautiful landscape with mountains",
                "shot_type": random.choice(["wide", "medium", "close-up"]),
                "camera_movement": random.choice(["static", "pan", "zoom"]),
                "duration": random.uniform(3, 6)
            }
            for i in range(1, 4)
        ]
        return json.dumps({"scenes": scenes}, ensure_ascii=False)
    
    async def check_health(self) -> bool:
        return True


class MockImageProvider(BaseImageProvider):
    """Mock 图片生成供应商"""
    
    MOCK_IMAGES = [
        "https://picsum.photos/1024/576",
        "https://picsum.photos/seed/scene1/1024/576",
        "https://picsum.photos/seed/scene2/1024/576",
        "https://picsum.photos/seed/scene3/1024/576",
    ]
    
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
        """模拟图片生成"""
        await asyncio.sleep(1)  # 模拟生成延迟
        
        seed = seed or random.randint(1, 100000)
        image_url = f"https://picsum.photos/seed/{seed}/{width}/{height}"
        
        logger.info("mock_image_generated", prompt=prompt[:50], seed=seed)
        
        return {
            "image_url": image_url,
            "task_id": f"mock-{seed}",
            "seed": seed,
            "all_images": [image_url]
        }
    
    async def check_health(self) -> bool:
        return True


class MockVideoProvider(BaseVideoProvider):
    """Mock 视频生成供应商"""
    
    # 一些公开的示例视频
    MOCK_VIDEOS = [
        "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "https://storage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    ]
    
    async def submit_task(
        self,
        image_url: str,
        prompt: str = "",
        duration: int = 5,
        **kwargs
    ) -> dict:
        """提交视频生成任务"""
        await asyncio.sleep(0.5)  # 模拟提交延迟
        
        task_id = f"mock-video-{random.randint(1000, 9999)}"
        logger.info("mock_video_task_submitted", image_url=image_url[:50], task_id=task_id)
        
        return {"task_id": task_id}
    
    async def get_task_status(self, task_id: str) -> dict:
        """获取任务状态"""
        return {
            "state": "completed",
            "progress": 100,
            "video_url": self.MOCK_VIDEOS[0],
            "error": None
        }
    
    async def generate(
        self,
        image_url: str,
        prompt: str = "",
        negative_prompt: str = "",
        duration: float = 5.0,
        mode: str = "std",
        cfg_scale: float = 0.5,
        **kwargs
    ) -> dict:
        """模拟视频生成"""
        await asyncio.sleep(2)  # 模拟生成延迟
        
        task_id = f"mock-video-{random.randint(1000, 9999)}"
        video_url = random.choice(self.MOCK_VIDEOS)
        
        logger.info("mock_video_generated", image_url=image_url[:50], task_id=task_id)
        
        return {
            "task_id": task_id,
            "video_url": video_url,
            "duration": duration
        }
    
    async def generate_text2video(
        self,
        prompt: str,
        negative_prompt: str = "",
        duration: float = 5.0,
        aspect_ratio: str = "16:9",
        mode: str = "std",
        **kwargs
    ) -> dict:
        """模拟文生视频"""
        await asyncio.sleep(2)
        
        task_id = f"mock-t2v-{random.randint(1000, 9999)}"
        video_url = random.choice(self.MOCK_VIDEOS)
        
        return {
            "task_id": task_id,
            "video_url": video_url,
            "duration": duration
        }
    
    async def check_health(self) -> bool:
        return True


class MockTTSProvider(BaseTTSProvider):
    """Mock TTS 供应商"""
    
    async def synthesize(
        self,
        text: str,
        voice: str = "default",
        format: str = "mp3",
        sample_rate: int = 16000,
        volume: int = 50,
        speech_rate: int = 0,
        pitch_rate: int = 0,
        **kwargs
    ) -> dict:
        """模拟语音合成"""
        await asyncio.sleep(0.5)
        
        # 返回一个简单的静音音频（实际项目中可以返回真实的测试音频）
        # 这里返回空字节，实际使用时前端需要处理
        duration = len(text) / 4  # 估算时长
        
        logger.info("mock_tts_synthesized", text_length=len(text), voice=voice)
        
        return {
            "audio_data": b"",  # 空音频数据
            "duration": duration,
            "format": format
        }
    
    async def get_voices(self) -> List[dict]:
        """获取可用音色"""
        return [
            {"id": "default", "name": "默认", "gender": "female", "language": "zh"},
            {"id": "male", "name": "男声", "gender": "male", "language": "zh"},
        ]
    
    async def check_health(self) -> bool:
        return True

