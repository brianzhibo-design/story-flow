"""
场景属性 Schema - 基于短剧创作实战优化

核心原则：光影统一性是画面真实感的关键
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class TimeOfDay(str, Enum):
    """时间段 - 影响光照"""
    DAWN = "dawn"           # 黎明 - 金色柔光
    MORNING = "morning"     # 清晨 - 明亮清新
    NOON = "noon"           # 正午 - 强烈顶光
    AFTERNOON = "afternoon" # 下午 - 暖色调
    GOLDEN_HOUR = "golden_hour"  # 黄金时刻 - 最佳拍摄
    DUSK = "dusk"           # 黄昏 - 橙红暖调
    NIGHT = "night"         # 夜晚 - 人工光源
    BLUE_HOUR = "blue_hour" # 蓝调时刻 - 冷色调
    MIDNIGHT = "midnight"   # 深夜 - 极暗


class Weather(str, Enum):
    """天气 - 影响氛围"""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    OVERCAST = "overcast"
    RAINY = "rainy"
    STORMY = "stormy"
    SNOWY = "snowy"
    FOGGY = "foggy"
    MISTY = "misty"
    WINDY = "windy"


class LightingType(str, Enum):
    """光照类型 - 电影级"""
    NATURAL = "natural light"
    CINEMATIC = "cinematic lighting"
    VOLUMETRIC = "volumetric lighting"
    RIM = "rim lighting"
    BACKLIT = "backlit"
    SIDE_LIT = "side lighting"
    TOP_LIT = "top lighting"
    NEON = "neon lighting"
    CANDLELIGHT = "candlelight"
    MOONLIGHT = "moonlight"
    GOLDEN = "golden hour lighting"
    DRAMATIC = "dramatic lighting"


class LocationAttributes(BaseModel):
    """
    场景属性 - 基于短剧创作实战优化
    
    核心原则：光影统一性是画面真实感的关键
    """
    
    # ==================== 基础分类 ====================
    location_type: Literal["interior", "exterior", "mixed"] = "interior"
    environment: Optional[str] = None  # urban/rural/nature/fantasy/sci-fi
    setting_era: Optional[str] = None  # ancient/medieval/modern/futuristic/cyberpunk
    
    # ==================== 具体地点 ====================
    place_type: Optional[str] = None  # 咖啡厅/古代街道/太空站
    place_details: Optional[str] = None  # 地点细节描述
    architecture_style: Optional[str] = None  # Chinese/Japanese/European/Modern
    
    # ==================== 时间与天气 ====================
    time_of_day: Optional[TimeOfDay] = None
    weather: Optional[Weather] = None
    season: Optional[str] = None  # spring/summer/autumn/winter
    
    # ==================== 光照系统（核心） ====================
    primary_lighting: Optional[LightingType] = None
    secondary_lighting: Optional[LightingType] = None
    light_direction: Optional[str] = None  # from_left/from_right/from_above/from_behind
    light_intensity: Optional[str] = None  # soft/medium/harsh
    light_color: Optional[str] = None  # warm_orange/cool_blue/neutral
    
    # ==================== 色调与氛围 ====================
    color_palette: list[str] = Field(default_factory=list)  # ["teal", "orange", "dark"]
    color_temperature: Optional[str] = None  # warm/neutral/cool
    color_grading: Optional[str] = None  # 调色风格：cinematic/vintage/vibrant
    mood: Optional[str] = None  # peaceful/tense/mysterious/romantic/melancholic
    atmosphere: Optional[str] = None  # 氛围特效：dusty/smoky/hazy
    
    # ==================== 空间构成 ====================
    camera_distance: Optional[str] = None  # extreme_close_up/close_up/medium/wide/extreme_wide
    depth_layers: Optional[str] = None  # 景深层次：foreground/midground/background
    perspective: Optional[str] = None  # eye_level/low_angle/high_angle/bird_eye/worm_eye
    
    # ==================== 场景元素 ====================
    key_elements: list[str] = Field(default_factory=list)  # 关键物体
    background_elements: list[str] = Field(default_factory=list)  # 背景元素
    foreground_elements: list[str] = Field(default_factory=list)  # 前景元素
    
    # ==================== 动态元素（视频用） ====================
    ambient_motion: list[str] = Field(default_factory=list)
    # 示例: ["leaves falling", "smoke rising", "rain drops", "crowd walking"]
    
    # ==================== 时代逻辑校验 ====================
    era_appropriate_items: list[str] = Field(default_factory=list)  # 符合时代的物品
    era_forbidden_items: list[str] = Field(default_factory=list)   # 禁止出现的物品
    # 示例：古代场景 era_forbidden_items = ["电线杆", "汽车", "手机"]
    
    def to_prompt(self) -> str:
        """生成英文提示词 - 遵循电影级场景构建"""
        parts = []
        
        # 1. 地点类型
        if self.place_type:
            parts.append(self.place_type)
        if self.place_details:
            parts.append(self.place_details)
        
        # 2. 建筑/环境风格
        if self.architecture_style:
            parts.append(f"{self.architecture_style} architecture")
        if self.environment:
            parts.append(f"{self.environment} environment")
        if self.setting_era:
            parts.append(f"{self.setting_era} era")
        
        # 3. 时间与天气
        if self.time_of_day:
            parts.append(self.time_of_day.value)
        if self.weather:
            parts.append(f"{self.weather.value} weather")
        if self.season:
            parts.append(self.season)
        
        # 4. 光照（核心）
        lighting = []
        if self.primary_lighting:
            lighting.append(self.primary_lighting.value)
        if self.secondary_lighting:
            lighting.append(self.secondary_lighting.value)
        if self.light_direction:
            lighting.append(f"light {self.light_direction}")
        if lighting:
            parts.append(", ".join(lighting))
        
        # 5. 色调与氛围
        if self.color_grading:
            parts.append(f"{self.color_grading} color grading")
        if self.mood:
            parts.append(f"{self.mood} mood")
        if self.atmosphere:
            parts.append(f"{self.atmosphere} atmosphere")
        
        # 6. 关键元素
        if self.key_elements:
            parts.append("with " + ", ".join(self.key_elements))
        
        # 7. 景深层次
        if self.camera_distance:
            parts.append(f"{self.camera_distance} shot")
        if self.perspective:
            parts.append(f"{self.perspective} view")
        
        return ", ".join(filter(None, parts))
    
    def get_lighting_prompt(self) -> str:
        """获取专门的光照提示词"""
        parts = []
        
        if self.primary_lighting:
            parts.append(self.primary_lighting.value)
        
        if self.time_of_day:
            time_light_map = {
                "dawn": "soft golden sunrise light",
                "morning": "bright morning light",
                "noon": "harsh overhead sunlight",
                "golden_hour": "warm golden hour sunlight",
                "dusk": "orange sunset light",
                "night": "artificial night lighting",
                "blue_hour": "cool blue twilight",
                "midnight": "dim moonlight"
            }
            parts.append(time_light_map.get(self.time_of_day.value, ""))
        
        if self.light_color:
            parts.append(f"{self.light_color} tones")
        
        return ", ".join(filter(None, parts))
    
    def validate_era_logic(self, items: list[str]) -> list[str]:
        """
        时代逻辑校验
        
        返回不符合时代的物品列表
        """
        violations = []
        forbidden_lower = [f.lower() for f in self.era_forbidden_items]
        for item in items:
            if item.lower() in forbidden_lower:
                violations.append(item)
        return violations
