"""
视频生成 Worker

将图片转换为视频
"""

import asyncio
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


class VideoTask(BaseWorkerTask):
    """视频生成任务"""
    
    name = "app.workers.video.generate_video"
    
    # 视频生成可能需要更长时间
    time_limit = 600  # 10分钟
    soft_time_limit = 540
    
    async def execute(
        self,
        db: AsyncSession,
        task_record: TaskModel,
        **kwargs
    ) -> dict[str, Any]:
        """执行视频生成"""
        
        # 获取分镜信息
        scene = await self._get_scene(db, task_record.scene_id)
        if not scene:
            raise ValueError("Scene not found")
        
        if not scene.image_url:
            raise ValueError("Scene has no image, generate image first")
        
        # 获取参数
        image_url = scene.image_url
        motion_prompt = kwargs.get("motion_prompt", "")
        duration = kwargs.get("duration", 5)
        provider_name = kwargs.get("provider", "kling")
        
        # 更新进度
        await self.update_progress(db, task_record, 5, "准备生成视频...")
        
        # 更新分镜状态
        scene.status = SceneStatus.GENERATING
        await db.commit()
        
        # 获取 AI 供应商
        router = AIProviderRouter()
        provider = await router.get_video_provider(provider_name)
        
        await self.update_progress(db, task_record, 10, f"提交到 {provider_name}...")
        
        # 提交视频生成任务
        submit_result = await provider.submit_task(
            image_url=image_url,
            prompt=motion_prompt,
            duration=duration
        )
        
        external_task_id = submit_result["task_id"]
        
        # 轮询等待完成
        video_url = await self._poll_until_complete(
            db=db,
            task_record=task_record,
            provider=provider,
            external_task_id=external_task_id,
            timeout=300
        )
        
        await self.update_progress(db, task_record, 90, "下载并上传视频...")
        
        # 上传到我们的存储
        final_url = await storage_client.upload_from_url(
            source_url=video_url,
            target_path=f"projects/{task_record.project_id}/scenes/{scene.id}/video.mp4"
        )
        
        # 更新分镜
        scene.video_url = final_url
        scene.duration = duration
        scene.status = SceneStatus.COMPLETED
        await db.commit()
        
        return {
            "video_url": final_url,
            "duration": duration,
            "provider": provider_name
        }
    
    async def _get_scene(self, db: AsyncSession, scene_id: UUID | None) -> Scene | None:
        """获取分镜"""
        if not scene_id:
            return None
        stmt = select(Scene).where(Scene.id == scene_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _poll_until_complete(
        self,
        db: AsyncSession,
        task_record: TaskModel,
        provider,
        external_task_id: str,
        timeout: int = 300
    ) -> str:
        """轮询等待视频生成完成"""
        import time
        
        start_time = time.time()
        poll_interval = 5  # 每5秒轮询一次
        
        while time.time() - start_time < timeout:
            # 查询状态
            status = await provider.get_task_status(external_task_id)
            
            if status["state"] == "completed":
                return status["video_url"]
            
            elif status["state"] == "failed":
                raise Exception(f"Video generation failed: {status.get('error', 'Unknown error')}")
            
            # 计算并更新进度 (10-90 之间)
            elapsed = time.time() - start_time
            progress = min(10 + int((elapsed / timeout) * 80), 89)
            
            await self.update_progress(
                db, task_record, progress,
                f"视频生成中... {int(elapsed)}秒"
            )
            
            # 等待下次轮询
            await asyncio.sleep(poll_interval)
        
        raise TimeoutError(f"Video generation timeout after {timeout}s")


# 注册任务
generate_video = celery_app.register_task(VideoTask())
