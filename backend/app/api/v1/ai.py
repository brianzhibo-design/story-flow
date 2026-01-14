"""
AI 相关 API 端点

包括分镜生成、图片生成、视频生成等
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List

from app.ai_gateway.router import get_ai_gateway
from app.services.storyboard_service import get_storyboard_service

router = APIRouter(prefix="/ai", tags=["AI"])


# ==================== 请求/响应模型 ====================

class StoryboardRequest(BaseModel):
    """分镜生成请求"""
    story_text: str = Field(..., min_length=10, description="故事文本")
    style: str = Field(default="电影", description="视觉风格")
    num_scenes: int = Field(default=10, ge=1, le=50, description="分镜数量")
    aspect_ratio: str = Field(default="16:9", description="画面比例")


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., min_length=1, description="用户消息")
    system_prompt: Optional[str] = Field(None, description="系统提示词")


class ImageRequest(BaseModel):
    """图片生成请求"""
    prompt: str = Field(..., min_length=1, description="正向提示词")
    negative_prompt: str = Field(default="", description="负向提示词")
    width: int = Field(default=1024, ge=256, le=2048)
    height: int = Field(default=576, ge=256, le=2048)
    style: Optional[str] = Field(None, description="风格预设")


class VideoRequest(BaseModel):
    """视频生成请求"""
    image_url: str = Field(..., description="输入图片 URL")
    prompt: str = Field(default="", description="运动提示词")
    duration: float = Field(default=5.0, ge=1, le=10, description="时长(秒)")


class TTSRequest(BaseModel):
    """语音合成请求"""
    text: str = Field(..., min_length=1, max_length=1000, description="待合成文本")
    voice: str = Field(default="zhixiaobai", description="音色")


# ==================== API 端点 ====================

@router.get("/health")
async def ai_health_check():
    """
    AI 服务健康检查
    
    检查所有 AI 供应商的可用状态
    """
    ai = get_ai_gateway()
    status = await ai.health_check()
    
    return {
        "code": 0,
        "message": "success",
        "data": status
    }


@router.post("/storyboard")
async def generate_storyboard(request: StoryboardRequest):
    """
    生成分镜脚本
    
    将故事文本转化为可视化分镜
    """
    service = get_storyboard_service()
    
    try:
        scenes = await service.generate_storyboard(
            story_text=request.story_text,
            style=request.style,
            num_scenes=request.num_scenes,
            aspect_ratio=request.aspect_ratio
        )
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "scenes": scenes,
                "total": len(scenes)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    AI 聊天
    
    与 LLM 进行对话
    """
    ai = get_ai_gateway()
    
    messages = []
    if request.system_prompt:
        messages.append({"role": "system", "content": request.system_prompt})
    messages.append({"role": "user", "content": request.message})
    
    try:
        response = await ai.chat(messages)
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "response": response
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image")
async def generate_image(request: ImageRequest):
    """
    生成图片
    
    使用通义万相或其他图片生成服务
    """
    ai = get_ai_gateway()
    
    try:
        result = await ai.generate_image(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            width=request.width,
            height=request.height,
            style=request.style
        )
        
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video")
async def generate_video(request: VideoRequest):
    """
    生成视频
    
    使用可灵将图片转换为视频
    """
    ai = get_ai_gateway()
    
    try:
        result = await ai.generate_video(
            image_url=request.image_url,
            prompt=request.prompt,
            duration=request.duration
        )
        
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts")
async def synthesize_speech(request: TTSRequest):
    """
    语音合成
    
    将文本转换为语音
    """
    ai = get_ai_gateway()
    
    try:
        result = await ai.synthesize_speech(
            text=request.text,
            voice=request.voice
        )
        
        # 注意：audio_data 是 bytes，这里返回时长信息
        # 实际使用时可能需要保存到存储后返回 URL
        return {
            "code": 0,
            "message": "success",
            "data": {
                "duration": result.get("duration", 0),
                "format": result.get("format", "mp3"),
                "size": len(result.get("audio_data", b""))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def get_voices():
    """
    获取可用音色列表
    """
    ai = get_ai_gateway()
    
    try:
        voices = await ai.get_voices()
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "voices": voices
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

