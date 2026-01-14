# backend/app/schemas/project.py
from typing import Optional, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.project import ProjectStatus


# === 请求模式 ===

class ProjectCreate(BaseModel):
    """创建项目请求"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    story_text: str = Field(..., min_length=10, max_length=50000)
    config: Optional[dict] = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    """更新项目请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    story_text: Optional[str] = Field(None, min_length=10, max_length=50000)
    config: Optional[dict] = None


class ProjectGenerate(BaseModel):
    """触发生成请求"""
    steps: Optional[list[str]] = Field(
        default=None,
        description="要执行的步骤，默认全部: storyboard, image, video, audio, compose"
    )
    force: bool = Field(
        default=False,
        description="是否强制重新生成"
    )


# === 响应模式 ===

class CharacterOut(BaseModel):
    """角色输出"""
    id: UUID
    name: str
    description: Optional[str] = None
    appearance: Optional[str] = None
    reference_image_url: Optional[str] = None
    
    model_config = {"from_attributes": True}


class ProjectOut(BaseModel):
    """项目输出"""
    id: UUID
    title: str
    description: Optional[str] = None
    status: ProjectStatus
    config: dict
    scene_count: int
    total_duration: int
    thumbnail_url: Optional[str] = None
    final_video_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ProjectDetail(ProjectOut):
    """项目详情（含故事文本）"""
    story_text: str
    characters: list[CharacterOut] = []


class ProjectListItem(BaseModel):
    """项目列表项"""
    id: UUID
    title: str
    status: ProjectStatus
    scene_count: int
    thumbnail_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class GenerateResponse(BaseModel):
    """生成任务响应"""
    project_id: UUID
    task_ids: list[UUID]
    estimated_time: Optional[int] = Field(None, description="预计时间（秒）")
