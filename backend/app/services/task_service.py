# backend/app/services/task_service.py
from uuid import UUID
from datetime import datetime
from typing import Optional

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskType, TaskStatus
from app.models.project import Project, ProjectStatus
from app.core.exceptions import TaskNotFoundError, ProjectNotFoundError
from app.core.redis import redis_client
import json


class TaskService:
    """任务服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        project_id: UUID,
        task_type: TaskType,
        payload: dict,
        scene_id: Optional[UUID] = None,
        priority: int = 0,
    ) -> Task:
        """
        创建任务。
        
        Args:
            project_id: 项目ID
            task_type: 任务类型
            payload: 任务参数
            scene_id: 分镜ID（可选）
            priority: 优先级
            
        Returns:
            创建的任务
        """
        task = Task(
            project_id=project_id,
            scene_id=scene_id,
            type=task_type,
            payload=payload,
            priority=priority,
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    async def get_by_id(self, task_id: UUID) -> Task:
        """
        通过ID获取任务。
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务对象
        """
        result = await self.db.execute(
            select(Task).where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if not task:
            raise TaskNotFoundError()
        
        return task
    
    async def get_project_tasks(
        self,
        project_id: UUID,
        task_type: Optional[TaskType] = None,
        status: Optional[TaskStatus] = None,
    ) -> list[Task]:
        """
        获取项目的任务列表。
        
        Args:
            project_id: 项目ID
            task_type: 类型筛选
            status: 状态筛选
            
        Returns:
            任务列表
        """
        conditions = [Task.project_id == project_id]
        
        if task_type:
            conditions.append(Task.type == task_type)
        if status:
            conditions.append(Task.status == status)
        
        result = await self.db.execute(
            select(Task)
            .where(and_(*conditions))
            .order_by(Task.created_at.desc())
        )
        
        return list(result.scalars().all())
    
    async def update_status(
        self,
        task_id: UUID,
        status: TaskStatus,
        progress: Optional[int] = None,
        result: Optional[dict] = None,
        error_message: Optional[str] = None,
    ) -> Task:
        """
        更新任务状态。
        
        Args:
            task_id: 任务ID
            status: 新状态
            progress: 进度
            result: 结果
            error_message: 错误信息
            
        Returns:
            更新后的任务
        """
        task = await self.get_by_id(task_id)
        
        task.status = status
        
        if progress is not None:
            task.progress = progress
        
        if result is not None:
            task.result = result
        
        if error_message is not None:
            task.error_message = error_message
        
        # 更新时间戳
        now = datetime.utcnow()
        if status == TaskStatus.QUEUED:
            task.queued_at = now
        elif status == TaskStatus.RUNNING:
            task.started_at = now
        elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
            task.completed_at = now
        
        await self.db.commit()
        await self.db.refresh(task)
        
        # 发送进度更新到Redis（供WebSocket推送）
        await self._publish_progress(task)
        
        return task
    
    async def _publish_progress(self, task: Task) -> None:
        """发布任务进度到Redis"""
        message = {
            "task_id": str(task.id),
            "project_id": str(task.project_id),
            "type": task.type.value,
            "status": task.status.value,
            "progress": task.progress,
        }
        
        if task.result:
            message["result"] = task.result
        if task.error_message:
            message["error"] = task.error_message
        
        await redis_client.publish(
            f"task:progress:{task.project_id}",
            json.dumps(message)
        )
    
    async def create_generation_tasks(
        self,
        project_id: UUID,
        steps: Optional[list[str]] = None,
    ) -> list[Task]:
        """
        创建项目生成任务。
        
        Args:
            project_id: 项目ID
            steps: 要执行的步骤
            
        Returns:
            创建的任务列表
        """
        # 获取项目
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        if not project:
            raise ProjectNotFoundError()
        
        # 默认所有步骤
        if not steps:
            steps = ["storyboard", "image", "video", "compose"]
        
        tasks = []
        
        # 分镜任务
        if "storyboard" in steps:
            task = await self.create(
                project_id=project_id,
                task_type=TaskType.STORYBOARD,
                payload={
                    "story_text": project.story_text,
                    "config": project.config,
                },
                priority=100,
            )
            tasks.append(task)
        
        # 更新项目状态
        project.status = ProjectStatus.PROCESSING
        await self.db.commit()
        
        return tasks
