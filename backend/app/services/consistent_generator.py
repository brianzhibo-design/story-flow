"""
一致性图片生成服务

整合元素管理、参考图、IP-Adapter 实现角色一致性
"""

import hashlib
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scene import Scene
from app.models.visual_element import VisualElement, ElementType
from app.services.element_service import ElementService
from app.services.file_service import get_file_service
from app.ai_gateway.router import AIProviderRouter
from app.config import settings


class ConsistentImageGenerator:
    """一致性图片生成器"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.element_service = ElementService(db)
        self.file_service = get_file_service()
        self.router = AIProviderRouter()
    
    async def generate_scene_image(
        self,
        scene: Scene,
        project_id: UUID,
        use_consistency: bool = True
    ) -> dict:
        """
        生成分镜图片
        
        自动处理角色一致性
        """
        # 1. 获取场景相关的元素
        all_elements = await self.element_service.get_project_elements(project_id)
        
        # 匹配角色
        characters = [
            e for e in all_elements
            if e.type == ElementType.CHARACTER.value and e.name in (scene.characters or [])
        ]
        
        # 匹配场景
        location = None
        
        # 匹配道具
        props = [
            e for e in all_elements
            if e.type == ElementType.PROP.value and e.name in (scene.props or [])
        ]
        
        # 获取风格
        style = next(
            (e for e in all_elements if e.type == ElementType.STYLE.value),
            None
        )
        
        # 2. 构建提示词
        prompt = self.element_service.build_scene_prompt(
            scene_description=scene.scene_description or scene.image_prompt or "",
            characters=characters,
            location=location,
            props=props,
            style=style
        )
        
        negative_prompt = self.element_service.build_negative_prompt(style)
        
        # 3. 获取参考图
        reference_images = []
        if use_consistency and characters:
            for char in characters:
                ref_url = await self.element_service.get_best_reference(char.id)
                if ref_url:
                    scale = char.consistency_config.get("ip_adapter_scale", 0.6) if char.consistency_config else 0.6
                    reference_images.append({
                        "element_id": str(char.id),
                        "image_url": ref_url,
                        "weight": scale
                    })
        
        # 4. 获取种子
        seed = self._get_scene_seed(scene, characters)
        
        # 5. 选择生成方式
        if reference_images and settings.COMFYUI_URL:
            # 使用 ComfyUI + IP-Adapter
            result = await self._generate_with_comfyui(
                prompt=prompt,
                negative_prompt=negative_prompt,
                references=reference_images,
                seed=seed
            )
        else:
            # 使用普通图片生成
            result = await self._generate_normal(
                prompt=prompt,
                negative_prompt=negative_prompt,
                seed=seed
            )
        
        # 6. 保存到存储
        saved = await self.file_service.save_scene_image(
            project_id=str(project_id),
            scene_id=str(scene.id),
            source_url=result["image_url"]
        )
        result["final_url"] = saved.url
        
        # 7. 保存元素出现记录
        for char in characters:
            await self.element_service.save_appearance(
                element_id=char.id,
                scene_id=scene.id,
                image_url=saved.url,
                generation_params={"seed": result.get("seed"), "prompt": prompt}
            )
        
        return result
    
    async def _generate_with_comfyui(
        self,
        prompt: str,
        negative_prompt: str,
        references: list[dict],
        seed: int
    ) -> dict:
        """使用 ComfyUI 生成"""
        from app.ai_gateway.providers.comfyui import ComfyUIProvider
        
        comfyui = ComfyUIProvider()
        
        if len(references) == 1:
            return await comfyui.generate_with_reference(
                prompt=prompt,
                reference_image_url=references[0]["image_url"],
                ip_adapter_scale=references[0]["weight"],
                negative_prompt=negative_prompt,
                seed=seed
            )
        else:
            return await comfyui.generate_with_multi_reference(
                prompt=prompt,
                references=references,
                negative_prompt=negative_prompt,
                seed=seed
            )
    
    async def _generate_normal(
        self,
        prompt: str,
        negative_prompt: str,
        seed: int
    ) -> dict:
        """普通生成"""
        provider = await self.router.get_image_provider()
        return await provider.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed
        )
    
    def _get_scene_seed(self, scene: Scene, characters: list[VisualElement]) -> int:
        """获取场景种子"""
        # 如果有主角且有固定种子，使用派生种子
        if characters:
            char = characters[0]
            config = char.consistency_config or {}
            base_seed = config.get("seed")
            if base_seed:
                return self._derive_seed(base_seed, scene.scene_index)
        
        return -1  # 随机种子
    
    def _derive_seed(self, base_seed: int, scene_index: int) -> int:
        """从基础种子派生场景种子"""
        data = f"{base_seed}:{scene_index}".encode()
        hash_val = int(hashlib.md5(data).hexdigest()[:8], 16)
        return hash_val % 2147483647

