"""
提示词融合服务

实现公式：完美画面 = 基础模型 × 精准提示词 × 参考图/ControlNet

基于《巨日禄 AI 短剧创作手记》实战经验优化
"""

from typing import Optional
from app.models.visual_element import VisualElement, ElementType
from app.schemas.elements import (
    CharacterAttributes, LocationAttributes, 
    CostumeAttributes, PropAttributes, StyleAttributes,
    ShotAttributes
)


class PromptFusionService:
    """
    提示词融合服务
    
    核心原则：
    1. 角色一致性锚点必须保留
    2. 光影必须统一
    3. 时代逻辑必须正确
    """
    
    # 质量增强词
    QUALITY_BOOSTERS = [
        "masterpiece", "best quality", "highly detailed",
        "8k uhd", "professional photography"
    ]
    
    # 通用负面提示词
    DEFAULT_NEGATIVE = (
        "blurry, low quality, deformed, ugly, bad anatomy, "
        "bad hands, extra fingers, missing fingers, "
        "watermark, signature, text, logo, "
        "duplicate, morbid, mutilated, poorly drawn"
    )
    
    def fuse_scene_prompt(
        self,
        scene_description: str,
        characters: list[VisualElement],
        location: Optional[VisualElement],
        costumes: list[VisualElement],
        props: list[VisualElement],
        style: Optional[VisualElement],
        shot: Optional[ShotAttributes] = None,
        character_states: Optional[dict] = None
    ) -> dict:
        """
        融合完整场景提示词
        
        Args:
            scene_description: 场景基础描述
            characters: 场景中的角色列表
            location: 场景地点
            costumes: 服装列表
            props: 道具列表
            style: 画面风格
            shot: 镜头属性
            character_states: 角色状态字典
                {
                    "char_id": {
                        "position": "left",
                        "action": "walking",
                        "expression": "smiling"
                    }
                }
        
        Returns:
            {
                "prompt": "完整正向提示词",
                "negative_prompt": "负面提示词",
                "warnings": ["时代冲突警告等"],
                "lighting_source": "光源方向",
                "generation_params": {...}
            }
        """
        parts = []
        warnings = []
        generation_params = {}
        
        # ==================== 1. 风格前缀 ====================
        style_attrs = None
        if style and style.attributes:
            style_attrs = StyleAttributes(**style.attributes)
            prefix = style_attrs.to_prompt_prefix()
            if prefix:
                parts.append(prefix)
            generation_params = style_attrs.get_generation_params()
        else:
            # 默认质量增强
            parts.extend(self.QUALITY_BOOSTERS[:3])
        
        # ==================== 2. 镜头信息 ====================
        if shot:
            shot_prompt = shot.to_prompt()
            if shot_prompt:
                parts.append(shot_prompt)
        
        # ==================== 3. 场景描述 ====================
        if scene_description:
            parts.append(scene_description)
        
        # ==================== 4. 场景地点与光照 ====================
        lighting_source = None
        if location and location.attributes:
            loc_attrs = LocationAttributes(**location.attributes)
            
            # 地点描述
            loc_prompt = loc_attrs.to_prompt()
            if loc_prompt:
                parts.append(loc_prompt)
            
            # 提取光照信息
            lighting_source = loc_attrs.get_lighting_prompt()
            if lighting_source:
                parts.append(lighting_source)
            
            # 时代逻辑校验
            all_items = [p.name for p in props]
            violations = loc_attrs.validate_era_logic(all_items)
            if violations:
                warnings.append(f"时代冲突警告：{', '.join(violations)} 不应出现在此场景")
        
        # ==================== 5. 角色描述（核心） ====================
        for i, char in enumerate(characters):
            if not char.attributes:
                continue
                
            char_attrs = CharacterAttributes(**char.attributes)
            
            # 优先使用一致性锚点
            if char_attrs.consistency_anchor:
                char_prompt = char_attrs.consistency_anchor
            else:
                char_prompt = char_attrs.to_prompt()
            
            if not char_prompt:
                continue
            
            # 角色状态（动作、表情）
            state = (character_states or {}).get(str(char.id), {})
            if state.get("action"):
                char_prompt += f", {state['action']}"
            if state.get("expression"):
                char_prompt += f", {state['expression']} expression"
            if state.get("position"):
                char_prompt += f", {state['position']} of frame"
            
            # 角色服装
            char_costume = next(
                (c for c in costumes if c.attributes and 
                 c.attributes.get("default_for_character_id") == str(char.id)),
                None
            )
            if char_costume and char_costume.attributes:
                costume_attrs = CostumeAttributes(**char_costume.attributes)
                costume_prompt = costume_attrs.to_prompt()
                if costume_prompt:
                    char_prompt += f", wearing {costume_prompt}"
            
            # 添加角色标记
            label = char.name or f"character_{i+1}"
            parts.append(f"[{label}] {char_prompt}")
        
        # ==================== 6. 道具 ====================
        if props:
            prop_prompts = []
            for prop in props:
                if prop.attributes:
                    prop_attrs = PropAttributes(**prop.attributes)
                    prop_prompt = prop_attrs.to_prompt()
                    if prop_prompt:
                        prop_prompts.append(f"{prop.name}: {prop_prompt}")
                else:
                    prop_prompts.append(prop.name)
            if prop_prompts:
                parts.append("with " + ", ".join(prop_prompts))
        
        # ==================== 7. 风格后缀 ====================
        if style_attrs:
            suffix = style_attrs.to_prompt_suffix()
            if suffix:
                parts.append(suffix)
        
        # ==================== 8. 光照统一性 ====================
        if lighting_source and characters:
            # 确保光照方向一致
            parts.append(f"consistent {lighting_source} on all subjects")
        
        # ==================== 构建最终提示词 ====================
        prompt = ", ".join(filter(None, parts))
        
        # 构建负面提示词
        negative = self.DEFAULT_NEGATIVE
        if style_attrs and style_attrs.negative_prompt_template:
            negative = style_attrs.negative_prompt_template
        
        return {
            "prompt": prompt,
            "negative_prompt": negative,
            "warnings": warnings,
            "lighting_source": lighting_source,
            "generation_params": generation_params
        }
    
    def fuse_video_prompt(
        self,
        image_prompt: str,
        shot: ShotAttributes,
        duration: float = 5.0
    ) -> dict:
        """
        融合视频生成提示词
        
        Args:
            image_prompt: 图片提示词
            shot: 镜头属性
            duration: 视频时长
        
        Returns:
            {
                "prompt": "视频提示词",
                "motion_prompt": "运动提示词",
                "motion_bucket_id": 127,
                "safe_intensity": 0.5,
                "duration": 5.0
            }
        """
        motion_prompt = shot.get_motion_prompt()
        safe_intensity = shot.get_safe_motion_intensity()
        motion_bucket_id = shot.get_motion_bucket_id()
        
        video_prompt = f"{image_prompt}, {motion_prompt}"
        
        return {
            "prompt": video_prompt,
            "motion_prompt": motion_prompt,
            "motion_bucket_id": motion_bucket_id,
            "safe_intensity": safe_intensity,
            "duration": duration
        }
    
    def fuse_character_portrait_prompt(
        self,
        character: VisualElement,
        costume: Optional[VisualElement] = None,
        expression: Optional[str] = None,
        pose: Optional[str] = None,
        style: Optional[VisualElement] = None
    ) -> dict:
        """
        生成角色肖像提示词（用于生成角色参考图）
        
        Returns:
            {
                "prompt": "角色肖像提示词",
                "negative_prompt": "负面提示词"
            }
        """
        parts = []
        
        # 风格前缀
        if style and style.attributes:
            style_attrs = StyleAttributes(**style.attributes)
            parts.append(style_attrs.to_prompt_prefix())
        else:
            parts.extend(self.QUALITY_BOOSTERS[:3])
        
        # 肖像类型
        parts.append("character portrait, upper body shot")
        
        # 角色描述
        if character.attributes:
            char_attrs = CharacterAttributes(**character.attributes)
            char_prompt = char_attrs.to_prompt()
            if char_prompt:
                parts.append(char_prompt)
        
        # 表情
        if expression:
            parts.append(f"{expression} expression")
        
        # 姿势
        if pose:
            parts.append(pose)
        
        # 服装
        if costume and costume.attributes:
            costume_attrs = CostumeAttributes(**costume.attributes)
            costume_prompt = costume_attrs.to_prompt()
            if costume_prompt:
                parts.append(f"wearing {costume_prompt}")
        
        # 背景
        parts.append("simple neutral background, studio lighting")
        
        prompt = ", ".join(filter(None, parts))
        
        return {
            "prompt": prompt,
            "negative_prompt": self.DEFAULT_NEGATIVE
        }
    
    def validate_scene_consistency(
        self,
        characters: list[VisualElement],
        location: Optional[VisualElement],
        props: list[VisualElement]
    ) -> list[str]:
        """
        验证场景一致性
        
        Returns:
            警告列表
        """
        warnings = []
        
        # 检查角色是否有一致性锚点
        for char in characters:
            if char.attributes:
                char_attrs = CharacterAttributes(**char.attributes)
                if not char_attrs.consistency_anchor:
                    warnings.append(
                        f"角色 '{char.name}' 缺少一致性锚点，建议调用 generate_consistency_anchor()"
                    )
        
        # 检查时代一致性
        if location and location.attributes:
            loc_attrs = LocationAttributes(**location.attributes)
            if loc_attrs.setting_era:
                for prop in props:
                    if prop.attributes:
                        prop_attrs = PropAttributes(**prop.attributes)
                        if prop_attrs.era and prop_attrs.era != loc_attrs.setting_era:
                            warnings.append(
                                f"道具 '{prop.name}' 的时代 ({prop_attrs.era}) "
                                f"与场景时代 ({loc_attrs.setting_era}) 不匹配"
                            )
        
        return warnings


# 全局实例
prompt_fusion_service = PromptFusionService()

