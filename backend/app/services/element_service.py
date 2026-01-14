"""
视觉元素服务

管理角色、场景、道具等视觉元素
"""

from typing import Optional
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.visual_element import VisualElement, ElementAppearance, ElementType
from app.schemas.elements import (
    CharacterAttributes, LocationAttributes, PropAttributes,
    CostumeAttributes, StyleAttributes
)


class ElementService:
    """视觉元素服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== 创建元素 ====================
    
    async def create_element(
        self,
        project_id: UUID,
        element_type: ElementType,
        name: str,
        attributes: dict,
        **kwargs
    ) -> VisualElement:
        """创建视觉元素"""
        
        # 根据类型生成提示词
        prompt_en = self._generate_prompt(element_type, attributes)
        
        element = VisualElement(
            project_id=project_id,
            type=element_type.value,
            name=name,
            attributes=attributes,
            prompt_en=prompt_en,
            **kwargs
        )
        self.db.add(element)
        await self.db.commit()
        await self.db.refresh(element)
        return element
    
    async def create_character(self, project_id: UUID, name: str, attrs: CharacterAttributes, **kwargs):
        return await self.create_element(project_id, ElementType.CHARACTER, name, attrs.model_dump(), **kwargs)
    
    async def create_location(self, project_id: UUID, name: str, attrs: LocationAttributes, **kwargs):
        return await self.create_element(project_id, ElementType.LOCATION, name, attrs.model_dump(), **kwargs)
    
    async def create_prop(self, project_id: UUID, name: str, attrs: PropAttributes, **kwargs):
        return await self.create_element(project_id, ElementType.PROP, name, attrs.model_dump(), **kwargs)
    
    async def create_costume(self, project_id: UUID, name: str, attrs: CostumeAttributes, **kwargs):
        return await self.create_element(project_id, ElementType.COSTUME, name, attrs.model_dump(), **kwargs)
    
    async def create_style(self, project_id: UUID, name: str, attrs: StyleAttributes, **kwargs):
        return await self.create_element(project_id, ElementType.STYLE, name, attrs.model_dump(), **kwargs)
    
    # ==================== 查询元素 ====================
    
    async def get_project_elements(
        self,
        project_id: UUID,
        element_type: Optional[ElementType] = None
    ) -> list[VisualElement]:
        """获取项目的所有元素"""
        stmt = select(VisualElement).where(
            VisualElement.project_id == project_id,
            VisualElement.is_active == True
        )
        if element_type:
            stmt = stmt.where(VisualElement.type == element_type.value)
        stmt = stmt.order_by(VisualElement.created_at)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_element_by_name(
        self,
        project_id: UUID,
        name: str
    ) -> Optional[VisualElement]:
        """根据名称获取元素"""
        stmt = select(VisualElement).where(
            VisualElement.project_id == project_id,
            VisualElement.name == name,
            VisualElement.is_active == True
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    # ==================== 参考图管理 ====================
    
    async def get_best_reference(self, element_id: UUID) -> Optional[str]:
        """获取元素的最佳参考图"""
        element = await self.db.get(VisualElement, element_id)
        if not element:
            return None
        
        # 优先用户上传的
        if element.primary_reference_url:
            return element.primary_reference_url
        
        # 从出现记录中找
        stmt = (
            select(ElementAppearance)
            .where(
                ElementAppearance.element_id == element_id,
                ElementAppearance.generated_image_url.isnot(None),
                ElementAppearance.is_reference_candidate == True
            )
            .order_by(ElementAppearance.quality_score.desc().nullslast())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        appearance = result.scalar_one_or_none()
        
        return appearance.generated_image_url if appearance else None
    
    async def save_appearance(
        self,
        element_id: UUID,
        scene_id: UUID,
        image_url: str,
        scene_state: dict = None,
        generation_params: dict = None
    ) -> ElementAppearance:
        """保存元素出现记录"""
        
        # 检查是否首次出现
        count_stmt = select(func.count()).where(ElementAppearance.element_id == element_id)
        count_result = await self.db.execute(count_stmt)
        is_first = (count_result.scalar() or 0) == 0
        
        appearance = ElementAppearance(
            element_id=element_id,
            scene_id=scene_id,
            generated_image_url=image_url,
            scene_state=scene_state or {},
            generation_params=generation_params or {},
            is_reference_candidate=is_first
        )
        self.db.add(appearance)
        
        # 更新使用次数
        element = await self.db.get(VisualElement, element_id)
        if element:
            element.usage_count += 1
        
        await self.db.commit()
        return appearance
    
    # ==================== 提示词生成 ====================
    
    def _generate_prompt(self, element_type: ElementType, attributes: dict) -> str:
        """根据类型生成提示词"""
        type_map = {
            ElementType.CHARACTER: CharacterAttributes,
            ElementType.LOCATION: LocationAttributes,
            ElementType.PROP: PropAttributes,
            ElementType.COSTUME: CostumeAttributes,
        }
        
        schema_class = type_map.get(element_type)
        if schema_class:
            attrs = schema_class(**attributes)
            return attrs.to_prompt()
        return ""
    
    def build_scene_prompt(
        self,
        scene_description: str,
        characters: list[VisualElement],
        location: Optional[VisualElement] = None,
        props: list[VisualElement] = None,
        style: Optional[VisualElement] = None,
        character_states: dict[str, dict] = None
    ) -> str:
        """构建完整的场景提示词"""
        parts = []
        
        # 1. 画风前缀
        if style:
            style_attrs = StyleAttributes(**style.attributes)
            prefix = style_attrs.to_prompt_prefix()
            if prefix:
                parts.append(prefix)
        
        # 2. 场景描述
        parts.append(scene_description)
        
        # 3. 场景地点
        if location and location.prompt_en:
            parts.append(f"in {location.prompt_en}")
        
        # 4. 角色描述
        for i, char in enumerate(characters):
            char_prompt = char.prompt_en or ""
            
            # 添加角色状态
            state = (character_states or {}).get(str(char.id), {})
            if state.get("action"):
                char_prompt += f", {state['action']}"
            if state.get("expression"):
                char_prompt += f", {state['expression']} expression"
            
            label = "main" if i == 0 else char.name
            parts.append(f"[{label}: {char.name}] {char_prompt}")
        
        # 5. 道具
        if props:
            prop_prompts = [f"{p.name}: {p.prompt_en}" for p in props if p.prompt_en]
            if prop_prompts:
                parts.append("with " + ", ".join(prop_prompts))
        
        # 6. 画风后缀
        if style:
            style_attrs = StyleAttributes(**style.attributes)
            suffix = style_attrs.to_prompt_suffix()
            if suffix:
                parts.append(suffix)
        
        return ", ".join(filter(None, parts))
    
    def build_negative_prompt(self, style: Optional[VisualElement] = None) -> str:
        """构建负面提示词"""
        default = "blurry, low quality, deformed, ugly, bad anatomy, bad hands"
        
        if style:
            template = style.attributes.get("negative_prompt_template")
            if template:
                return template
        
        return default

