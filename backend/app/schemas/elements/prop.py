"""
道具属性 Schema - 基于短剧创作实战优化
"""

from pydantic import BaseModel, Field
from typing import Optional


class PropAttributes(BaseModel):
    """
    道具属性
    
    包括可交互物品、场景装饰等
    """
    
    # ==================== 基础分类 ====================
    category: Optional[str] = None  # weapon/tool/furniture/decoration/vehicle
    subcategory: Optional[str] = None  # sword/hammer/chair/vase/car
    
    # ==================== 物理属性 ====================
    material: Optional[str] = None  # metal/wood/glass/fabric/plastic
    texture: Optional[str] = None  # smooth/rough/polished/weathered
    size: Optional[str] = None  # small/medium/large/massive
    weight_impression: Optional[str] = None  # light/heavy/bulky
    
    # ==================== 外观属性 ====================
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    pattern: Optional[str] = None  # solid/striped/patterned/gradient
    finish: Optional[str] = None  # matte/glossy/metallic/worn
    
    # ==================== 状态属性 ====================
    condition: Optional[str] = None  # new/used/damaged/ancient/rusted
    cleanliness: Optional[str] = None  # clean/dusty/dirty/bloodstained
    
    # ==================== 时代属性 ====================
    era: Optional[str] = None  # ancient/medieval/modern/futuristic
    cultural_origin: Optional[str] = None  # Chinese/Japanese/European/Middle Eastern
    
    # ==================== 功能属性 ====================
    is_magical: bool = False
    magical_effects: list[str] = Field(default_factory=list)  # glowing/floating/smoking
    is_interactive: bool = True  # 是否可交互
    
    # ==================== 详细描述 ====================
    description: Optional[str] = None
    distinctive_features: list[str] = Field(default_factory=list)
    
    def to_prompt(self) -> str:
        """生成道具提示词"""
        parts = []
        
        # 状态和条件
        if self.condition:
            parts.append(self.condition)
        
        # 颜色和材质
        if self.primary_color:
            parts.append(self.primary_color)
        if self.material:
            parts.append(self.material)
        
        # 纹理和表面
        if self.finish:
            parts.append(self.finish)
        if self.texture:
            parts.append(f"{self.texture} texture")
        
        # 尺寸
        if self.size:
            parts.append(self.size)
        
        # 类别
        if self.subcategory:
            parts.append(self.subcategory)
        elif self.category:
            parts.append(self.category)
        
        # 时代和文化
        if self.era:
            parts.append(f"{self.era} style")
        if self.cultural_origin:
            parts.append(f"{self.cultural_origin} design")
        
        # 特殊效果
        if self.is_magical and self.magical_effects:
            parts.append(", ".join(self.magical_effects))
        
        # 显著特征
        if self.distinctive_features:
            parts.append(", ".join(self.distinctive_features))
        
        return ", ".join(filter(None, parts))
