"""
角色属性 Schema - 基于短剧创作实战优化

核心原则：保持角色一致性（Consistency）是短剧的核心
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class AgeRange(str, Enum):
    """年龄段"""
    CHILD = "child"           # 儿童 (5-12)
    TEENAGER = "teenager"     # 青少年 (13-19)
    YOUNG_ADULT = "young_adult"  # 青年 (20-30)
    ADULT = "adult"           # 成年 (30-45)
    MIDDLE_AGED = "middle_aged"  # 中年 (45-60)
    ELDERLY = "elderly"       # 老年 (60+)


class BodyType(str, Enum):
    """体型"""
    SLIM = "slim"
    AVERAGE = "average"
    ATHLETIC = "athletic"
    MUSCULAR = "muscular"
    CURVY = "curvy"
    HEAVYSET = "heavyset"


class CharacterAttributes(BaseModel):
    """
    角色属性 - 基于短剧创作实战优化
    
    核心原则：保持角色一致性（Consistency）是短剧的核心
    """
    
    # ==================== 基础身份 ====================
    role_type: Literal["protagonist", "antagonist", "supporting", "extra"] = "supporting"
    character_archetype: Optional[str] = None  # 角色原型：英雄/导师/反派/丑角
    
    # ==================== 人物设定 ====================
    gender: Optional[Literal["male", "female", "other"]] = None
    age_range: Optional[AgeRange] = None
    age_specific: Optional[int] = None  # 具体年龄（如果需要精确）
    ethnicity: Optional[str] = None  # 民族/种族外观
    nationality_appearance: Optional[str] = None  # 国籍外观特征
    
    # ==================== 身体特征 ====================
    body_type: Optional[BodyType] = None
    height_description: Optional[str] = None  # tall/average/short
    skin_tone: Optional[str] = None  # fair/tan/dark/pale
    skin_texture: Optional[str] = None  # smooth/freckled/weathered
    
    # ==================== 面部特征（核心一致性） ====================
    face_shape: Optional[str] = None  # oval/round/square/heart
    eye_color: Optional[str] = None
    eye_shape: Optional[str] = None  # almond/round/monolid/hooded
    eyebrow_style: Optional[str] = None  # thick/thin/arched
    nose_type: Optional[str] = None  # straight/button/aquiline
    lip_shape: Optional[str] = None  # full/thin/cupid's bow
    jaw_line: Optional[str] = None  # sharp/soft/square
    
    # ==================== 面部标记（关键识别特征） ====================
    facial_marks: list[str] = Field(default_factory=list)
    # 示例: ["scar across left cheek", "beauty mark near lip", "birthmark on forehead"]
    
    # ==================== 发型（高频变化但需一致） ====================
    hair_color: Optional[str] = None
    hair_length: Optional[str] = None  # short/medium/long/bald
    hair_style: Optional[str] = None  # straight/wavy/curly/braided
    hair_texture: Optional[str] = None  # silky/coarse/frizzy
    facial_hair: Optional[str] = None  # beard/mustache/stubble/clean-shaven
    
    # ==================== 职业/身份外观 ====================
    occupation: Optional[str] = None  # 职业
    occupation_attire: Optional[str] = None  # 职业装扮
    social_class: Optional[str] = None  # 社会阶层外观
    era: Optional[str] = None  # 时代背景：ancient/medieval/modern/futuristic
    
    # ==================== 默认状态 ====================
    default_expression: Optional[str] = None  # neutral/smiling/serious/melancholic
    default_posture: Optional[str] = None  # standing/sitting/confident/slouched
    personality_vibe: Optional[str] = None  # 性格气质：cold/warm/mysterious/cheerful
    
    # ==================== 特殊配饰（固定标识） ====================
    signature_accessories: list[str] = Field(default_factory=list)
    # 示例: ["silver pendant necklace", "round glasses", "jade bracelet"]
    
    # ==================== 一致性锚点（核心 Prompt 片段） ====================
    consistency_anchor: Optional[str] = None
    # 这是保持角色一致的核心描述，每次生成必须包含
    # 示例: "30-year-old Asian woman with long black hair, almond eyes, beauty mark near left eye"
    
    def to_prompt(self) -> str:
        """生成英文提示词 - 遵循短剧创作最佳实践"""
        # 1. 一致性锚点优先
        if self.consistency_anchor:
            return self.consistency_anchor
        
        parts = []
        
        # 2. 构建基础描述
        basic = []
        if self.age_specific:
            basic.append(f"{self.age_specific}-year-old")
        elif self.age_range:
            age_map = {
                "child": "young child",
                "teenager": "teenage",
                "young_adult": "young adult",
                "adult": "adult",
                "middle_aged": "middle-aged",
                "elderly": "elderly"
            }
            basic.append(age_map.get(self.age_range.value, ""))
        
        if self.ethnicity:
            basic.append(self.ethnicity)
        if self.gender:
            basic.append("man" if self.gender == "male" else "woman" if self.gender == "female" else "person")
        
        if basic:
            parts.append(" ".join(basic))
        
        # 3. 身体特征
        body = []
        if self.body_type:
            body.append(f"{self.body_type.value} build")
        if self.height_description:
            body.append(self.height_description)
        if self.skin_tone:
            body.append(f"{self.skin_tone} skin")
        if body:
            parts.append(", ".join(body))
        
        # 4. 面部特征（核心）
        face = []
        if self.face_shape:
            face.append(f"{self.face_shape} face")
        if self.eye_color and self.eye_shape:
            face.append(f"{self.eye_color} {self.eye_shape} eyes")
        elif self.eye_color:
            face.append(f"{self.eye_color} eyes")
        if self.nose_type:
            face.append(f"{self.nose_type} nose")
        if self.lip_shape:
            face.append(f"{self.lip_shape} lips")
        if self.jaw_line:
            face.append(f"{self.jaw_line} jawline")
        if face:
            parts.append(", ".join(face))
        
        # 5. 面部标记（关键识别）
        if self.facial_marks:
            parts.append(", ".join(self.facial_marks))
        
        # 6. 发型
        hair = []
        if self.hair_length:
            hair.append(self.hair_length)
        if self.hair_color:
            hair.append(self.hair_color)
        if self.hair_style:
            hair.append(self.hair_style)
        if hair:
            parts.append(" ".join(hair) + " hair")
        if self.facial_hair:
            parts.append(self.facial_hair)
        
        # 7. 标志性配饰
        if self.signature_accessories:
            parts.append("wearing " + ", ".join(self.signature_accessories))
        
        # 8. 表情和气质
        if self.default_expression:
            parts.append(f"{self.default_expression} expression")
        if self.personality_vibe:
            parts.append(f"{self.personality_vibe} demeanor")
        
        return ", ".join(filter(None, parts))
    
    def generate_consistency_anchor(self) -> str:
        """
        自动生成一致性锚点
        
        这是角色的"身份证"，每次生成必须包含的核心描述
        """
        core_features = []
        
        # 年龄 + 性别 + 民族
        if self.age_specific and self.gender:
            ethnicity = self.ethnicity or ""
            gender_word = "man" if self.gender == "male" else "woman"
            core_features.append(f"{self.age_specific}-year-old {ethnicity} {gender_word}".strip())
        elif self.age_range and self.gender:
            age_map = {
                "child": "young",
                "teenager": "teenage",
                "young_adult": "young adult",
                "adult": "adult",
                "middle_aged": "middle-aged",
                "elderly": "elderly"
            }
            ethnicity = self.ethnicity or ""
            gender_word = "man" if self.gender == "male" else "woman"
            age_str = age_map.get(self.age_range.value, "")
            core_features.append(f"{age_str} {ethnicity} {gender_word}".strip())
        
        # 发型（高识别度）
        if self.hair_color and self.hair_length:
            core_features.append(f"{self.hair_length} {self.hair_color} hair")
        
        # 眼睛
        if self.eye_color:
            core_features.append(f"{self.eye_color} eyes")
        
        # 面部标记（最高识别度）
        if self.facial_marks:
            core_features.append(self.facial_marks[0])  # 最显著的标记
        
        # 标志性配饰
        if self.signature_accessories:
            core_features.append(self.signature_accessories[0])
        
        anchor = ", ".join(core_features)
        self.consistency_anchor = anchor
        return anchor
