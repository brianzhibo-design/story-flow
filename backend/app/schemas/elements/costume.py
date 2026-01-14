"""
服装属性 Schema - 基于短剧创作实战优化
"""

from pydantic import BaseModel, Field
from typing import Optional


class CostumeAttributes(BaseModel):
    """
    服装属性
    
    角色在不同场景可能穿着不同服装
    """
    
    # ==================== 基础分类 ====================
    garment_type: Optional[str] = None  # dress/suit/robe/armor/casual
    style: Optional[str] = None  # formal/casual/traditional/futuristic
    
    # ==================== 时代与文化 ====================
    era: Optional[str] = None  # ancient/medieval/modern/futuristic
    cultural_style: Optional[str] = None  # Chinese hanfu/Japanese kimono/Western suit
    
    # ==================== 颜色与面料 ====================
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    fabric: Optional[str] = None  # silk/cotton/leather/velvet/denim
    pattern: Optional[str] = None  # solid/striped/floral/plaid/embroidered
    
    # ==================== 装饰细节 ====================
    embellishments: list[str] = Field(default_factory=list)
    # 示例: ["gold buttons", "lace trim", "embroidered dragons"]
    
    # ==================== 配饰 ====================
    accessories: list[str] = Field(default_factory=list)
    # 示例: ["belt", "scarf", "gloves", "hat"]
    
    # ==================== 状态 ====================
    condition: Optional[str] = None  # pristine/worn/torn/bloodstained
    fit: Optional[str] = None  # tight/fitted/loose/oversized
    
    # ==================== 角色关联 ====================
    default_for_character_id: Optional[str] = None  # 默认属于哪个角色
    scene_specific: bool = False  # 是否场景特定服装
    
    def to_prompt(self) -> str:
        """生成服装提示词"""
        parts = []
        
        # 状态
        if self.condition and self.condition != "pristine":
            parts.append(self.condition)
        
        # 颜色
        colors = []
        if self.primary_color:
            colors.append(self.primary_color)
        if self.secondary_color:
            colors.append(self.secondary_color)
        if colors:
            parts.append(" and ".join(colors))
        
        # 面料和图案
        if self.pattern:
            parts.append(self.pattern)
        if self.fabric:
            parts.append(self.fabric)
        
        # 服装类型
        if self.garment_type:
            parts.append(self.garment_type)
        
        # 风格
        if self.cultural_style:
            parts.append(self.cultural_style)
        elif self.style:
            parts.append(f"{self.style} style")
        
        # 时代
        if self.era:
            parts.append(f"{self.era} era")
        
        # 装饰
        if self.embellishments:
            parts.append("with " + ", ".join(self.embellishments))
        
        # 配饰
        if self.accessories:
            parts.append("wearing " + ", ".join(self.accessories))
        
        return ", ".join(filter(None, parts))
