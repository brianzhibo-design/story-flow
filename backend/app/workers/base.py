"""
Worker 基类

提供所有 Worker 的通用功能
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from contextlib import asynccontextmanager

import structlog
from celery import Task
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.core.redis import redis_client
from app.models.task import Task as TaskModel, TaskStatus
import json

logger = structlog.get_logger()


@asynccontextmanager
async def get_db_context():
    """获取数据库会话上下文"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class BaseWorkerTask(Task, ABC):
    """
    Worker 任务基类
    
    所有 Worker 任务都应继承此类
    """
    
    # 任务配置
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    max_retries = 3
    
    # 绑定实例
    bind = True
    
    @abstractmethod
    async def execute(
        self,
        db: AsyncSession,
        task_record: TaskModel,
        **kwargs
    ) -> dict[str, Any]:
        """
        执行任务的具体逻辑
        
        子类必须实现此方法
        
        Args:
            db: 数据库会话
            task_record: 任务记录
            **kwargs: 任务参数
            
        Returns:
            任务结果字典
        """
        pass
    
    def run(self, task_id: str, **kwargs) -> dict[str, Any]:
        """
        Celery 任务入口
        
        Args:
            task_id: 数据库中的任务ID
            **kwargs: 任务参数
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._run_async(task_id, **kwargs))
        finally:
            loop.close()
    
    async def _run_async(self, task_id: str, **kwargs) -> dict[str, Any]:
        """异步执行任务"""
        async with get_db_context() as db:
            # 获取任务记录
            task_record = await self._get_task_record(db, task_id)
            if not task_record:
                logger.error("task_not_found", task_id=task_id)
                return {"error": "Task not found"}
            
            try:
                # 更新任务状态为运行中
                await self._update_task_status(
                    db, task_record,
                    status=TaskStatus.RUNNING,
                    started_at=datetime.utcnow(),
                    worker_id=self.request.hostname if self.request else None
                )
                
                # 执行具体任务
                result = await self.execute(db, task_record, **kwargs)
                
                # 更新任务状态为完成
                await self._update_task_status(
                    db, task_record,
                    status=TaskStatus.COMPLETED,
                    completed_at=datetime.utcnow(),
                    progress=100,
                    result=result
                )
                
                return result
                
            except Exception as e:
                logger.exception("task_execution_error", task_id=task_id, error=str(e))
                
                # 更新任务状态为失败
                await self._update_task_status(
                    db, task_record,
                    status=TaskStatus.FAILED,
                    completed_at=datetime.utcnow(),
                    error_message=str(e),
                    retry_count=task_record.retry_count + 1
                )
                
                # 判断是否重试
                if task_record.retry_count < task_record.max_retries:
                    raise self.retry(exc=e)
                
                return {"error": str(e)}
    
    async def _get_task_record(self, db: AsyncSession, task_id: str) -> Optional[TaskModel]:
        """获取任务记录"""
        from sqlalchemy import select
        stmt = select(TaskModel).where(TaskModel.id == UUID(task_id))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _update_task_status(
        self,
        db: AsyncSession,
        task_record: TaskModel,
        **updates
    ) -> None:
        """更新任务状态"""
        for key, value in updates.items():
            setattr(task_record, key, value)
        await db.commit()
        
        # 发布进度更新到 Redis
        if "progress" in updates or "status" in updates:
            await self._publish_progress(task_record)
    
    async def _publish_progress(self, task_record: TaskModel) -> None:
        """发布进度到 Redis (用于 WebSocket 推送)"""
        channel = f"task:progress:{task_record.project_id}"
        
        message = {
            "task_id": str(task_record.id),
            "type": task_record.type.value if hasattr(task_record.type, 'value') else task_record.type,
            "status": task_record.status.value if hasattr(task_record.status, 'value') else task_record.status,
            "progress": task_record.progress,
        }
        
        if task_record.result:
            message["result"] = task_record.result
        if task_record.error_message:
            message["error"] = task_record.error_message
        
        await redis_client.publish(channel, json.dumps(message))
    
    async def update_progress(
        self,
        db: AsyncSession,
        task_record: TaskModel,
        progress: int,
        message: str = ""
    ) -> None:
        """
        更新任务进度
        
        供子类调用
        """
        task_record.progress = progress
        await db.commit()
        await self._publish_progress(task_record)


class TaskHelper:
    """任务辅助函数"""
    
    @staticmethod
    async def create_task(
        db: AsyncSession,
        project_id: UUID,
        task_type: str,
        payload: dict,
        scene_id: Optional[UUID] = None,
        priority: int = 5
    ) -> TaskModel:
        """创建任务记录"""
        from app.models.task import Task, TaskType, TaskStatus
        
        task = Task(
            project_id=project_id,
            scene_id=scene_id,
            type=TaskType(task_type),
            status=TaskStatus.PENDING,
            priority=priority,
            payload=payload
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
    
    @staticmethod
    def dispatch_task(task_record: TaskModel) -> str:
        """分发任务到 Celery"""
        from app.workers.celery_app import celery_app
        from app.models.task import TaskType
        
        # 根据任务类型选择队列
        task_map = {
            TaskType.STORYBOARD: "app.workers.storyboard.generate_storyboard",
            TaskType.IMAGE: "app.workers.image.generate_image",
            TaskType.VIDEO: "app.workers.video.generate_video",
            TaskType.COMPOSE: "app.workers.compose.compose_video",
        }
        
        task_name = task_map.get(task_record.type)
        if not task_name:
            raise ValueError(f"Unknown task type: {task_record.type}")
        
        # 发送任务
        result = celery_app.send_task(
            task_name,
            args=[str(task_record.id)],
            kwargs=task_record.payload or {},
            task_id=f"celery-{task_record.id}"
        )
        
        return result.id
