# backend/app/models/task.py
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import enum

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Enum as SQLEnum
from app.models.base import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.scene import Scene


class TaskType(str, enum.Enum):
    """任务类型"""
    STORYBOARD = "storyboard"  # 分镜生成
    IMAGE = "image"            # 图片生成
    VIDEO = "video"            # 视频生成
    AUDIO = "audio"            # 音频生成
    COMPOSE = "compose"        # 合成


class TaskStatus(str, enum.Enum):
    """任务状态"""
    PENDING = "pending"       # 待处理
    QUEUED = "queued"         # 已入队
    RUNNING = "running"       # 运行中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败
    CANCELLED = "cancelled"   # 已取消


class Task(BaseModel):
    """任务模型"""
    
    __tablename__ = "tasks"
    
    # 关联
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    scene_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("scenes.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # 类型和状态
    type: Mapped[TaskType] = mapped_column(
        SQLEnum(TaskType),
        nullable=False,
        index=True,
    )
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus),
        default=TaskStatus.PENDING,
        nullable=False,
        index=True,
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="优先级，越大越高",
    )
    
    # 数据
    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="输入参数",
    )
    result: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="输出结果",
    )
    
    # 执行信息
    worker_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="执行的Worker ID",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="进度 0-100",
    )
    
    # 重试
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=3,
    )
    
    # 时间追踪
    queued_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # 关系
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="tasks",
    )
    
    @property
    def duration(self) -> Optional[float]:
        """计算执行时长（秒）"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def __repr__(self) -> str:
        return f"<Task {self.type} {self.status}>"
