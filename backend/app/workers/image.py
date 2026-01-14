"""
图片生成 Worker

调用 AI 生成分镜图片
"""

from typing import Any
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scene import Scene, SceneStatus
from app.models.task import Task as TaskModel
from app.workers.base import BaseWorkerTask
from app.workers.celery_app import celery_app
from app.ai_gateway.router import AIProviderRouter
from app.core.storage import storage_client

logger = structlog.get_logger()


class ImageTask(BaseWorkerTask):
    """图片生成任务"""
    
    name = "app.workers.image.generate_image"
    
    async def execute(
        self,
        db: AsyncSession,
        task_record: TaskModel,
        **kwargs
    ) -> dict[str, Any]:
        """执行图片生成"""
        
        # 获取分镜信息
        scene = await self._get_scene(db, task_record.scene_id)
        if not scene:
            raise ValueError("Scene not found")
        
        # 获取参数
        prompt = kwargs.get("prompt") or scene.image_prompt
        negative_prompt = kwargs.get("negative_prompt") or scene.negative_prompt or ""
        width = kwargs.get("width", 1024)
        height = kwargs.get("height", 576)  # 16:9
        provider_name = kwargs.get("provider", "jimeng")
        
        if not prompt:
            raise ValueError("No image prompt provided")
        
        # 更新进度
        await self.update_progress(db, task_record, 10, "准备生成图片...")
        
        # 更新分镜状态
        scene.status = SceneStatus.GENERATING
        await db.commit()
        
        # 获取 AI 供应商
        router = AIProviderRouter()
        provider = await router.get_image_provider(provider_name)
        
        await self.update_progress(db, task_record, 20, f"使用 {provider_name} 生成中...")
        
        # 调用图片生成 API
        result = await provider.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height
        )
        
        await self.update_progress(db, task_record, 70, "上传图片...")
        
        # 上传到存储
        if result.get("image_url"):
            image_url = await storage_client.upload_from_url(
                source_url=result["image_url"],
                target_path=f"projects/{task_record.project_id}/scenes/{scene.id}/image.png"
            )
        else:
            image_url = result.get("image_url", "")
        
        # 更新分镜
        scene.image_url = image_url
        scene.status = SceneStatus.COMPLETED
        await db.commit()
        
        return {
            "image_url": image_url,
            "seed": result.get("seed"),
            "provider": provider_name
        }
    
    async def _get_scene(self, db: AsyncSession, scene_id: UUID | None) -> Scene | None:
        """获取分镜"""
        if not scene_id:
            return None
        stmt = select(Scene).where(Scene.id == scene_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


# 注册任务
generate_image = celery_app.register_task(ImageTask())
