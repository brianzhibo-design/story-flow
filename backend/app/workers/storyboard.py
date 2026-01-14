"""
分镜生成 Worker

将故事文本拆解为分镜脚本
"""

import json
from typing import Any
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, Character
from app.models.scene import Scene, SceneStatus
from app.models.task import Task as TaskModel
from app.workers.base import BaseWorkerTask
from app.workers.celery_app import celery_app
from app.ai_gateway.providers.deepseek import DeepSeekProvider

logger = structlog.get_logger()


class StoryboardTask(BaseWorkerTask):
    """分镜生成任务"""
    
    name = "app.workers.storyboard.generate_storyboard"
    
    async def execute(
        self,
        db: AsyncSession,
        task_record: TaskModel,
        **kwargs
    ) -> dict[str, Any]:
        """执行分镜生成"""
        
        # 获取项目信息
        project = await self._get_project(db, task_record.project_id)
        if not project:
            raise ValueError("Project not found")
        
        story_text = project.story_text
        style_config = project.config.get("style", {}) if project.config else {}
        
        # 更新进度
        await self.update_progress(db, task_record, 10, "正在分析故事文本...")
        
        # 构建提示词
        prompt = self._build_prompt(story_text, style_config)
        
        # 调用 LLM
        await self.update_progress(db, task_record, 30, "AI 正在生成分镜脚本...")
        
        llm = DeepSeekProvider()
        response = await llm.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        # 解析结果
        await self.update_progress(db, task_record, 70, "正在解析分镜数据...")
        
        result_data = self._parse_response(response)
        scenes_data = result_data.get("scenes", [])
        characters_data = result_data.get("characters", [])
        
        # 保存分镜
        await self.update_progress(db, task_record, 85, "正在保存分镜...")
        
        scenes = await self._save_scenes(db, project.id, scenes_data)
        characters = await self._save_characters(db, project.id, characters_data)
        
        # 更新项目统计
        project.scene_count = len(scenes)
        await db.commit()
        
        return {
            "scene_count": len(scenes),
            "character_count": len(characters),
            "scene_ids": [str(s.id) for s in scenes]
        }
    
    async def _get_project(self, db: AsyncSession, project_id: UUID) -> Project | None:
        """获取项目"""
        stmt = select(Project).where(Project.id == project_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    def _build_prompt(self, story_text: str, style_config: dict) -> str:
        """构建分镜生成提示词"""
        return f"""你是一位专业的分镜脚本编剧。请将以下故事文本拆解为详细的分镜脚本。

## 故事文本
{story_text}

## 输出要求
请以 JSON 格式输出，包含以下结构：

{{
    "scenes": [
        {{
            "scene_index": 1,
            "text": "旁白或对话内容",
            "scene_description": "场景的详细视觉描述",
            "characters": ["角色名1", "角色名2"],
            "props": ["道具1", "道具2"],
            "camera_type": "medium",
            "mood": "紧张",
            "image_prompt": "用于AI绘图的英文提示词，包含场景、角色、构图、光影等细节"
        }}
    ],
    "characters": [
        {{
            "name": "角色名",
            "description": "角色简介",
            "appearance": "外观描述（发型、服装、特征等）",
            "prompt_template": "用于保持角色一致性的提示词模板"
        }}
    ]
}}

## 注意事项
1. 每个分镜的 text 控制在 50 字以内，适合 5-8 秒的视频
2. scene_description 要详细，包含背景、光线、氛围
3. image_prompt 必须是英文，要具体且有画面感
4. 保持角色描述的一致性
5. 合理安排景别变化，避免单调

请开始生成分镜："""
    
    def _parse_response(self, response: str) -> dict:
        """解析 LLM 响应"""
        try:
            # 尝试直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            # 尝试提取 JSON 部分
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError("Failed to parse LLM response as JSON")
    
    async def _save_scenes(
        self,
        db: AsyncSession,
        project_id: UUID,
        scenes_data: list[dict]
    ) -> list[Scene]:
        """保存分镜到数据库"""
        scenes = []
        
        for data in scenes_data:
            scene = Scene(
                project_id=project_id,
                scene_index=data.get("scene_index", len(scenes) + 1),
                text=data.get("text", ""),
                scene_description=data.get("scene_description", ""),
                characters=data.get("characters", []),
                props=data.get("props", []),
                camera_type=data.get("camera_type"),
                mood=data.get("mood"),
                image_prompt=data.get("image_prompt"),
                status=SceneStatus.PENDING
            )
            db.add(scene)
            scenes.append(scene)
        
        await db.flush()
        return scenes
    
    async def _save_characters(
        self,
        db: AsyncSession,
        project_id: UUID,
        characters_data: list[dict]
    ) -> list[Character]:
        """保存角色到数据库"""
        characters = []
        
        for data in characters_data:
            character = Character(
                project_id=project_id,
                name=data.get("name", ""),
                description=data.get("description", ""),
                appearance=data.get("appearance", ""),
                prompt_template=data.get("prompt_template", "")
            )
            db.add(character)
            characters.append(character)
        
        await db.flush()
        return characters


# 注册任务
generate_storyboard = celery_app.register_task(StoryboardTask())
