# backend/app/models/__init__.py
"""
数据模型模块。

导出所有 SQLAlchemy 模型以便 Alembic 和其他模块使用。
"""

from app.models.base import BaseModel, TimestampMixin, UUIDMixin
from app.models.user import User, UserQuota, UserRole, UserStatus, PlanType
from app.models.project import Project, Character, ProjectStatus
from app.models.scene import Scene, SceneStatus
from app.models.task import Task, TaskType, TaskStatus
from app.models.asset import Asset, AssetType
from app.models.visual_element import VisualElement, ElementAppearance, ElementType

__all__ = [
    # Base
    "BaseModel",
    "TimestampMixin",
    "UUIDMixin",
    # User
    "User",
    "UserQuota",
    "UserRole",
    "UserStatus",
    "PlanType",
    # Project
    "Project",
    "Character",
    "ProjectStatus",
    # Scene
    "Scene",
    "SceneStatus",
    # Task
    "Task",
    "TaskType",
    "TaskStatus",
    # Asset
    "Asset",
    "AssetType",
    # Visual Elements
    "VisualElement",
    "ElementAppearance",
    "ElementType",
]
