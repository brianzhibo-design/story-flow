"""
风格属性 Schema - 基于短剧创作实战优化
"""

from pydantic import BaseModel, Field
from typing import Optional


class StyleAttributes(BaseModel):
    """
    画面风格属性
    
    控制整体视觉风格、调色、后期效果
    """
    
    # ==================== 艺术风格 ====================
    art_style: Optional[str] = None
    # realistic/anime/cartoon/oil_painting/watercolor/cyberpunk/noir
    
    rendering_style: Optional[str] = None
    # photorealistic/3d_render/2d_illustration/pixel_art
    
    # ==================== 调色风格 ====================
    color_grading: Optional[str] = None
    # cinematic/vintage/vibrant/muted/high_contrast/desaturated
    
    color_temperature: Optional[str] = None  # warm/neutral/cool
    
    contrast: Optional[str] = None  # low/medium/high
    saturation: Optional[str] = None  # low/normal/high/vivid
    
    # ==================== 参考影片 ====================
    film_reference: Optional[str] = None
    # 示例: "Blade Runner 2049", "Wong Kar-wai style", "Wes Anderson palette"
    
    # ==================== 质量参数 ====================
    detail_level: Optional[str] = None  # low/medium/high/ultra
    
    # ==================== 生成参数 ====================
    cfg_scale: float = Field(default=7.0, ge=1.0, le=20.0)
    # 提示词遵循度：越高越遵循提示词，但可能过度饱和
    
    steps: int = Field(default=30, ge=10, le=100)
    # 采样步数
    
    sampler: Optional[str] = None
    # euler_ancestral/dpm++_2m/dpm++_sde/ddim
    
    # ==================== LoRA 模型 ====================
    lora_models: list[dict] = Field(default_factory=list)
    # [{"name": "add_detail", "weight": 0.8}, {"name": "film_grain", "weight": 0.3}]
    
    # ==================== 负面提示词模板 ====================
    negative_prompt_template: Optional[str] = None
    # 可自定义负面提示词
    
    # ==================== 质量增强词 ====================
    quality_boosters: list[str] = Field(
        default_factory=lambda: [
            "masterpiece", "best quality", "highly detailed"
        ]
    )
    
    def to_prompt_prefix(self) -> str:
        """生成风格前缀提示词"""
        parts = []
        
        # 质量增强词
        if self.quality_boosters:
            parts.extend(self.quality_boosters[:3])
        
        # 艺术风格
        if self.art_style:
            style_map = {
                "realistic": "photorealistic, hyperrealistic",
                "anime": "anime style, cel shaded",
                "cartoon": "cartoon style, vibrant colors",
                "oil_painting": "oil painting style, thick brushstrokes",
                "watercolor": "watercolor painting, soft edges",
                "cyberpunk": "cyberpunk style, neon lights",
                "noir": "film noir style, high contrast black and white"
            }
            parts.append(style_map.get(self.art_style, self.art_style))
        
        # 渲染风格
        if self.rendering_style:
            render_map = {
                "photorealistic": "photorealistic rendering",
                "3d_render": "3D rendered, octane render",
                "2d_illustration": "2D illustration",
                "pixel_art": "pixel art style"
            }
            parts.append(render_map.get(self.rendering_style, self.rendering_style))
        
        # 影片参考
        if self.film_reference:
            parts.append(f"in the style of {self.film_reference}")
        
        return ", ".join(filter(None, parts))
    
    def to_prompt_suffix(self) -> str:
        """生成风格后缀提示词"""
        parts = []
        
        # 调色
        if self.color_grading:
            grading_map = {
                "cinematic": "cinematic color grading",
                "vintage": "vintage color palette, faded colors",
                "vibrant": "vibrant saturated colors",
                "muted": "muted desaturated tones",
                "high_contrast": "high contrast, deep blacks",
                "desaturated": "desaturated, almost monochrome"
            }
            parts.append(grading_map.get(self.color_grading, f"{self.color_grading} color grading"))
        
        # 色温
        if self.color_temperature:
            temp_map = {
                "warm": "warm color temperature",
                "neutral": "neutral colors",
                "cool": "cool color temperature"
            }
            parts.append(temp_map.get(self.color_temperature, ""))
        
        # 细节等级
        if self.detail_level:
            detail_map = {
                "low": "",
                "medium": "detailed",
                "high": "highly detailed, intricate details",
                "ultra": "extremely detailed, intricate, 8K UHD"
            }
            parts.append(detail_map.get(self.detail_level, ""))
        
        return ", ".join(filter(None, parts))
    
    def get_generation_params(self) -> dict:
        """获取生成参数"""
        params = {
            "cfg_scale": self.cfg_scale,
            "steps": self.steps,
        }
        
        if self.sampler:
            params["sampler"] = self.sampler
        
        if self.lora_models:
            params["lora_models"] = self.lora_models
        
        return params
