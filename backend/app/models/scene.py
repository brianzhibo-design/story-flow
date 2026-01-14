# backend/app/models/scene.py
"""
分镜模型 - 基于短剧创作实战优化

新增字段支持：
- 镜头控制（类型、角度、运动）
- 角色状态（位置、动作、表情）
- 光照信息
- 画质增强记录
- 修改历史
"""

from typing import Optional, TYPE_CHECKING
from decimal import Decimal
import enum

from sqlalchemy import String, Text, Integer, Float, Boolean, Numeric, ForeignKey, UniqueConstraint, Enum as SQLEnum
from app.models.base import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.project import Project


class SceneStatus(str, enum.Enum):
    """分镜状态"""
    PENDING = "pending"       # 待处理
    GENERATING = "generating" # 生成中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败


class Scene(BaseModel):
    """
    分镜模型
    
    支持专业级镜头控制和画质增强
    """
    
    __tablename__ = "scenes"
    __table_args__ = (
        UniqueConstraint("project_id", "scene_index", name="uq_scene_project_index"),
    )
    
    # 关联
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    scene_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    
    # 内容
    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="旁白/对话文本",
    )
    scene_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="场景描述",
    )
    
    # 元素 (JSONB)
    characters: Mapped[list] = mapped_column(
        JSONB,
        default=list,
        comment="出场角色",
    )
    props: Mapped[list] = mapped_column(
        JSONB,
        default=list,
        comment="道具",
    )
    
    # ==================== 镜头控制 ====================
    camera_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="景别: 远景/中景/近景/特写",
    )
    mood: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="情绪",
    )
    
    # 镜头类型 (ShotType)
    shot_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="镜头类型: extreme_close_up/close_up/medium_shot/wide_shot",
    )
    
    # 机位角度 (CameraAngle)
    camera_angle: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="机位角度: eye_level/low_angle/high_angle/dutch_angle",
    )
    
    # 镜头运动 (CameraMovement)
    camera_movement: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="镜头运动: static/zoom_in/zoom_out/pan_left/pan_right",
    )
    
    # 运动强度
    movement_intensity: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="运动强度: 0-1，特写镜头自动降低",
    )
    
    # Motion Bucket ID (视频生成参数)
    motion_bucket_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Motion Bucket ID: 0-255，127为中等运动",
    )
    
    # ==================== 角色状态 ====================
    character_states: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment='''角色状态: {
            "char_id": {
                "position": "left/center/right",
                "action": "walking/sitting/standing",
                "expression": "smiling/crying/angry",
                "costume_id": "costume_xxx"
            }
        }''',
    )
    
    # ==================== 光照信息 ====================
    lighting_info: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment='''光照信息: {
            "primary": "cinematic lighting",
            "direction": "from_left/from_right/from_above",
            "color": "warm_orange/cool_blue/neutral"
        }''',
    )
    
    # ==================== 画质增强 ====================
    is_face_enhanced: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否已进行面部增强",
    )
    is_hand_enhanced: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否已进行手部增强",
    )
    is_upscaled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否已超分",
    )
    original_image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="增强前原图URL",
    )
    
    # ==================== 修改历史 ====================
    edit_history: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        comment='''修改历史: [
            {"type": "inpaint", "region": {...}, "prompt": "...", "timestamp": "..."},
            {"type": "upscale", "factor": 2, "timestamp": "..."},
            {"type": "face_fix", "timestamp": "..."}
        ]''',
    )
    
    # AI 提示词
    image_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    negative_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # 生成结果
    image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    video_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    audio_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    
    # 时长
    duration: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2),
        nullable=True,
        comment="时长（秒）",
    )
    
    # 状态
    status: Mapped[SceneStatus] = mapped_column(
        SQLEnum(SceneStatus),
        default=SceneStatus.PENDING,
        nullable=False,
    )
    
    # 关系
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="scenes",
    )
    
    def __repr__(self) -> str:
        return f"<Scene {self.project_id}#{self.scene_index}>"
