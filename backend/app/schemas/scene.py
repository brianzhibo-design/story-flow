# backend/app/schemas/scene.py
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field

from app.models.scene import SceneStatus


# === 请求模式 ===

class SceneCreate(BaseModel):
    """创建分镜请求"""
    scene_index: int = Field(..., ge=0)
    text: str = Field(..., min_length=1, max_length=1000)
    scene_description: Optional[str] = Field(None, max_length=2000)
    characters: list[str] = Field(default_factory=list)
    props: list[str] = Field(default_factory=list)
    camera_type: Optional[str] = Field(None, max_length=50)
    mood: Optional[str] = Field(None, max_length=50)
    image_prompt: Optional[str] = None
    negative_prompt: Optional[str] = None


class SceneUpdate(BaseModel):
    """更新分镜请求"""
    text: Optional[str] = Field(None, min_length=1, max_length=1000)
    scene_description: Optional[str] = Field(None, max_length=2000)
    characters: Optional[list[str]] = None
    props: Optional[list[str]] = None
    camera_type: Optional[str] = Field(None, max_length=50)
    mood: Optional[str] = Field(None, max_length=50)
    image_prompt: Optional[str] = None
    negative_prompt: Optional[str] = None


class SceneRegenerate(BaseModel):
    """重新生成请求"""
    type: str = Field(..., pattern="^(image|video|audio)$")
    prompt_override: Optional[str] = None


class SceneBatchCreate(BaseModel):
    """批量创建分镜请求"""
    scenes: list[SceneCreate]


# === 响应模式 ===

class SceneOut(BaseModel):
    """分镜输出"""
    id: UUID
    project_id: UUID
    scene_index: int
    text: str
    scene_description: Optional[str] = None
    characters: list[str]
    props: list[str]
    camera_type: Optional[str] = None
    mood: Optional[str] = None
    image_prompt: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    duration: Optional[Decimal] = None
    status: SceneStatus
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class SceneListOut(BaseModel):
    """分镜列表输出"""
    scenes: list[SceneOut]
    total: int
