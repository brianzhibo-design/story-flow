"""
视觉元素模型

存储角色、场景、道具、服装、风格等视觉元素
"""

from enum import Enum
from sqlalchemy import ForeignKey, String, Text, Boolean, Integer, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, JSONB


class ElementType(str, Enum):
    """元素类型"""
    CHARACTER = "character"
    LOCATION = "location"
    PROP = "prop"
    COSTUME = "costume"
    STYLE = "style"


class VisualElement(BaseModel):
    """视觉元素表"""
    
    __tablename__ = "visual_elements"
    
    # 关联
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    
    # 基本信息
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    
    # 提示词
    prompt_cn: Mapped[str | None] = mapped_column(Text)
    prompt_en: Mapped[str | None] = mapped_column(Text)
    negative_prompt: Mapped[str | None] = mapped_column(Text)
    
    # 参考图
    reference_images: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    primary_reference_url: Mapped[str | None] = mapped_column(String(500))
    
    # 一致性配置
    consistency_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # {"seed": 12345, "ip_adapter_scale": 0.6, "locked": false}
    
    # 扩展属性（各类型特有）
    attributes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    tags: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    
    # 关系
    project: Mapped["Project"] = relationship("Project", back_populates="visual_elements")
    appearances: Mapped[list["ElementAppearance"]] = relationship(
        "ElementAppearance", back_populates="element", cascade="all, delete-orphan"
    )


class ElementAppearance(BaseModel):
    """元素出现记录"""
    
    __tablename__ = "element_appearances"
    
    # 关联
    element_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("visual_elements.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    scene_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("scenes.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    
    # 场景内状态
    scene_state: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # 角色: {"position": "center", "action": "walking", "expression": "smile"}
    # 场景: {"time_override": "night"}
    
    # 生成结果
    generated_image_url: Mapped[str | None] = mapped_column(String(500))
    cropped_region: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # 生成参数
    generation_params: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # 质量评估
    quality_score: Mapped[float | None] = mapped_column(Float)
    consistency_score: Mapped[float | None] = mapped_column(Float)
    is_reference_candidate: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 关系
    element: Mapped["VisualElement"] = relationship("VisualElement", back_populates="appearances")
    scene: Mapped["Scene"] = relationship("Scene")

