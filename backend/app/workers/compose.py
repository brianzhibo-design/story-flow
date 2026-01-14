"""
视频合成任务

将所有分镜合成为最终视频
"""

from uuid import UUID
import structlog

from app.workers.celery_app import celery_app
from app.workers.base import BaseTask
from app.models.project import Project, ProjectStatus
from app.models.scene import Scene, SceneStatus
from app.models.task import Task, TaskType, TaskStatus
from app.services.video_composer import VideoComposer
from sqlalchemy import select

logger = structlog.get_logger()


class ComposeTask(BaseTask):
    """视频合成任务基类"""
    pass


@celery_app.task(base=ComposeTask, bind=True, name="app.workers.compose.compose_video")
def compose_video(self, project_id: str, task_id: str) -> dict:
    """
    合成项目最终视频
    """
    import asyncio
    return asyncio.get_event_loop().run_until_complete(
        _compose_video_async(self, project_id, task_id)
    )


async def _compose_video_async(task_instance, project_id: str, task_id: str) -> dict:
    """异步合成视频"""
    from app.core.database import async_session_maker
    
    async with async_session_maker() as db:
        # 获取项目和任务
        project = await db.get(Project, UUID(project_id))
        task = await db.get(Task, UUID(task_id))
        
        if not project or not task:
            logger.error("compose_not_found", project_id=project_id, task_id=task_id)
            return {"error": "Not found"}
        
        try:
            # 更新任务状态
            task.status = TaskStatus.STARTED
            await db.commit()
            
            # 获取所有已完成的分镜
            stmt = (
                select(Scene)
                .where(
                    Scene.project_id == project.id,
                    Scene.status == SceneStatus.COMPLETED
                )
                .order_by(Scene.scene_index)
            )
            result = await db.execute(stmt)
            scenes = result.scalars().all()
            
            if not scenes:
                raise Exception("No completed scenes to compose")
            
            # 准备分镜数据
            scene_data = []
            for scene in scenes:
                data = {
                    "video_url": scene.video_url,
                    "audio_url": scene.audio_url,
                    "duration": scene.duration or 5,
                    "text": scene.text
                }
                # 如果没有视频，跳过
                if scene.video_url:
                    scene_data.append(data)
            
            # 获取合成配置
            config = project.config.get("compose", {}) if project.config else {}
            
            # 合成
            composer = VideoComposer()
            result = await composer.compose_project(
                project_id=project_id,
                scenes=scene_data,
                config=config
            )
            
            # 更新项目
            project.final_video_url = result["video_url"]
            project.status = ProjectStatus.COMPLETED
            
            # 更新任务
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.progress = 1.0
            
            await db.commit()
            
            logger.info("compose_completed", project_id=project_id, video_url=result["video_url"])
            
            return result
            
        except Exception as e:
            logger.error("compose_failed", project_id=project_id, error=str(e))
            
            # 更新状态
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            project.status = ProjectStatus.FAILED
            await db.commit()
            
            raise
