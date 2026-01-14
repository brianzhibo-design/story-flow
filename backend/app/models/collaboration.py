"""
协作与分享模型

支持:
- 项目分享链接
- 协作者管理
- 评论系统
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.models.base import JSONB
from datetime import datetime
from typing import Optional
import enum

from app.models.base import Base, TimestampMixin, UUIDMixin


class ShareType(enum.Enum):
    """分享权限类型"""
    VIEW = "view"       # 仅查看
    COMMENT = "comment" # 可评论
    EDIT = "edit"       # 可编辑


class CollaboratorRole(enum.Enum):
    """协作者角色"""
    VIEWER = "viewer"
    COMMENTER = "commenter"
    EDITOR = "editor"
    ADMIN = "admin"


class ProjectShare(Base, UUIDMixin, TimestampMixin):
    """项目分享链接"""
    __tablename__ = "project_shares"
    
    project_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("projects.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # 分享链接
    share_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    share_type: Mapped[ShareType] = mapped_column(
        SQLEnum(ShareType), 
        default=ShareType.VIEW
    )
    
    # 标题 (可自定义)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # 密码保护
    password_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    # 有效期
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 访问限制
    max_views: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # 是否允许下载
    allow_download: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 创建者
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    
    # 关系
    project = relationship("Project", back_populates="shares")
    creator = relationship("User")


class ProjectCollaborator(Base, UUIDMixin, TimestampMixin):
    """项目协作者"""
    __tablename__ = "project_collaborators"
    
    project_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("projects.id", ondelete="CASCADE"), 
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # 角色权限
    role: Mapped[CollaboratorRole] = mapped_column(
        SQLEnum(CollaboratorRole), 
        default=CollaboratorRole.VIEWER
    )
    
    # 邀请信息
    invited_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    invited_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 接受状态
    is_accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 邀请邮件/链接
    invite_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    invite_code: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, unique=True)
    
    # 关系
    project = relationship("Project", back_populates="collaborators")
    user = relationship("User", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])
    
    # 唯一约束
    __table_args__ = (
        # 同一用户不能重复添加到同一项目
        {"extend_existing": True},
    )


class ProjectComment(Base, UUIDMixin, TimestampMixin):
    """项目评论"""
    __tablename__ = "project_comments"
    
    project_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("projects.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    scene_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("scenes.id", ondelete="CASCADE"), 
        nullable=True,
        index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id"), 
        nullable=False
    )
    
    # 评论内容
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 回复
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("project_comments.id", ondelete="CASCADE"), 
        nullable=True
    )
    
    # 时间戳标记 (视频评论)
    timestamp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 秒
    
    # 标注位置 (图片评论)
    position_x: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 百分比
    position_y: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # 状态
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolved_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # 软删除
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 关系
    project = relationship("Project")
    scene = relationship("Scene")
    user = relationship("User")
    replies = relationship(
        "ProjectComment",
        backref="parent",
        remote_side="ProjectComment.id",
        lazy="selectin"
    )


class ActivityLog(Base, UUIDMixin):
    """协作活动日志"""
    __tablename__ = "activity_logs"
    
    project_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("projects.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id"), 
        nullable=False
    )
    
    # 活动类型
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    # create_project, update_project, add_scene, update_scene, 
    # generate_image, generate_video, add_comment, invite_collaborator, etc.
    
    # 目标
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # 详情
    details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # 时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    project = relationship("Project")
    user = relationship("User")

