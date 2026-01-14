# backend/app/models/project.py
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import enum

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Enum as SQLEnum
from app.models.base import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.scene import Scene
    from app.models.task import Task
    from app.models.visual_element import VisualElement
    from app.models.collaboration import ProjectShare, ProjectCollaborator


class ProjectStatus(str, enum.Enum):
    """项目状态"""
    DRAFT = "draft"           # 草稿
    PROCESSING = "processing" # 处理中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败


class Project(BaseModel):
    """项目模型"""
    
    __tablename__ = "projects"
    
    # 基本信息
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    story_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    # 状态
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.DRAFT,
        nullable=False,
        index=True,
    )
    
    # 配置 (JSONB)
    config: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
    
    # 统计
    scene_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    total_duration: Mapped[int] = mapped_column(
        Integer,
        default=0,  # 秒
    )
    
    # 输出
    final_video_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    thumbnail_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    
    # 软删除
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # 关系
    user: Mapped["User"] = relationship(
        "User",
        back_populates="projects",
    )
    scenes: Mapped[list["Scene"]] = relationship(
        "Scene",
        back_populates="project",
        order_by="Scene.scene_index",
        lazy="selectin",
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="project",
        lazy="selectin",
    )
    characters: Mapped[list["Character"]] = relationship(
        "Character",
        back_populates="project",
        lazy="selectin",
    )
    visual_elements: Mapped[list["VisualElement"]] = relationship(
        "VisualElement",
        back_populates="project",
        lazy="selectin",
    )
    shares: Mapped[list["ProjectShare"]] = relationship(
        "ProjectShare",
        back_populates="project",
        lazy="selectin",
    )
    collaborators: Mapped[list["ProjectCollaborator"]] = relationship(
        "ProjectCollaborator",
        back_populates="project",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<Project {self.title}>"


class Character(BaseModel):
    """角色模型"""
    
    __tablename__ = "characters"
    
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    appearance: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    reference_image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    prompt_template: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # 关系
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="characters",
    )
    
    def __repr__(self) -> str:
        return f"<Character {self.name}>"
