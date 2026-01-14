# backend/app/schemas/task.py
from typing import Optional, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

from app.models.task import TaskType, TaskStatus


# === 响应模式 ===

class TaskOut(BaseModel):
    """任务输出"""
    id: UUID
    project_id: UUID
    scene_id: Optional[UUID] = None
    type: TaskType
    status: TaskStatus
    progress: int
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    
    model_config = {"from_attributes": True}


class TaskDetail(TaskOut):
    """任务详情（含payload和result）"""
    payload: dict
    result: Optional[dict] = None


class TaskListOut(BaseModel):
    """任务列表输出"""
    tasks: list[TaskOut]
    total: int


class TaskProgress(BaseModel):
    """任务进度（WebSocket推送）"""
    task_id: UUID
    project_id: UUID
    type: TaskType
    status: TaskStatus
    progress: int
    message: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None
