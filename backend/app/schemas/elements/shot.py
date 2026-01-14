"""
镜头与运动控制 Schema - 基于短剧创作实战

核心原则：镜头运动幅度控制，避免面部崩坏
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class ShotType(str, Enum):
    """镜头类型"""
    EXTREME_CLOSE_UP = "extreme_close_up"  # 特写（眼睛、手）
    CLOSE_UP = "close_up"                   # 近景（脸部）
    MEDIUM_CLOSE_UP = "medium_close_up"     # 中近景（胸部以上）
    MEDIUM_SHOT = "medium_shot"             # 中景（腰部以上）
    MEDIUM_WIDE = "medium_wide"             # 中全景（膝盖以上）
    WIDE_SHOT = "wide_shot"                 # 全景（全身）
    EXTREME_WIDE = "extreme_wide"           # 大远景
    ESTABLISHING = "establishing"           # 建立镜头


class CameraAngle(str, Enum):
    """机位角度"""
    EYE_LEVEL = "eye_level"       # 平视
    LOW_ANGLE = "low_angle"       # 仰拍
    HIGH_ANGLE = "high_angle"     # 俯拍
    BIRD_EYE = "bird_eye"         # 鸟瞰
    WORM_EYE = "worm_eye"         # 蚁视
    DUTCH_ANGLE = "dutch_angle"   # 倾斜（不安感）
    OVER_SHOULDER = "over_shoulder"  # 过肩镜头
    POV = "pov"                   # 主观视角


class CameraMovement(str, Enum):
    """镜头运动 - 图生视频核心"""
    STATIC = "static"             # 静止
    ZOOM_IN = "zoom_in"           # 推镜头
    ZOOM_OUT = "zoom_out"         # 拉镜头
    PAN_LEFT = "pan_left"         # 左摇
    PAN_RIGHT = "pan_right"       # 右摇
    TILT_UP = "tilt_up"           # 上摇
    TILT_DOWN = "tilt_down"       # 下摇
    TRUCK_LEFT = "truck_left"     # 左移
    TRUCK_RIGHT = "truck_right"   # 右移
    DOLLY_IN = "dolly_in"         # 推进
    DOLLY_OUT = "dolly_out"       # 拉出
    CRANE_UP = "crane_up"         # 升
    CRANE_DOWN = "crane_down"     # 降
    ORBIT = "orbit"               # 环绕
    FOLLOW = "follow"             # 跟随


class ShotAttributes(BaseModel):
    """
    镜头属性 - 基于短剧创作实战
    
    核心原则：镜头运动幅度控制，避免面部崩坏
    """
    
    # ==================== 镜头基础 ====================
    shot_type: Optional[ShotType] = None
    camera_angle: Optional[CameraAngle] = None
    
    # ==================== 镜头运动（视频用） ====================
    camera_movement: Optional[CameraMovement] = None
    movement_speed: Optional[Literal["slow", "medium", "fast"]] = "medium"
    movement_intensity: Optional[float] = Field(default=0.5, ge=0, le=1)
    # 运动幅度：0-1，越大运动越明显，但面部崩坏风险越高
    
    # ==================== 运动参数（Motion Bucket） ====================
    motion_bucket_id: Optional[int] = Field(default=127, ge=0, le=255)
    # 127 为中等运动，0 为静止，255 为剧烈运动
    
    # ==================== 焦点控制 ====================
    focus_point: Optional[str] = None  # 焦点位置：center/left/right/face
    depth_of_field: Optional[str] = None  # shallow/deep/selective
    bokeh: Optional[bool] = False  # 背景虚化
    
    # ==================== 画面构图 ====================
    composition: Optional[str] = None  # rule_of_thirds/center/golden_ratio/symmetry
    headroom: Optional[str] = None  # 头顶空间
    lead_room: Optional[str] = None  # 前进方向空间
    
    # ==================== 转场 ====================
    transition_in: Optional[str] = None  # fade_in/cut/dissolve/wipe
    transition_out: Optional[str] = None
    
    def to_prompt(self) -> str:
        """生成镜头提示词"""
        parts = []
        
        if self.shot_type:
            shot_map = {
                "extreme_close_up": "extreme close-up shot",
                "close_up": "close-up shot",
                "medium_close_up": "medium close-up",
                "medium_shot": "medium shot",
                "medium_wide": "medium wide shot",
                "wide_shot": "wide shot",
                "extreme_wide": "extreme wide shot, epic scale",
                "establishing": "establishing shot"
            }
            parts.append(shot_map.get(self.shot_type.value, ""))
        
        if self.camera_angle:
            angle_map = {
                "eye_level": "eye level",
                "low_angle": "low angle, looking up",
                "high_angle": "high angle, looking down",
                "bird_eye": "bird's eye view",
                "worm_eye": "worm's eye view",
                "dutch_angle": "dutch angle, tilted",
                "over_shoulder": "over the shoulder shot",
                "pov": "POV, first person view"
            }
            parts.append(angle_map.get(self.camera_angle.value, ""))
        
        if self.depth_of_field:
            if self.depth_of_field == "shallow":
                parts.append("shallow depth of field, bokeh background")
            elif self.depth_of_field == "deep":
                parts.append("deep focus, everything sharp")
        
        if self.composition:
            comp_map = {
                "rule_of_thirds": "rule of thirds composition",
                "center": "centered composition",
                "golden_ratio": "golden ratio composition",
                "symmetry": "symmetrical composition"
            }
            parts.append(comp_map.get(self.composition, ""))
        
        return ", ".join(filter(None, parts))
    
    def get_motion_prompt(self) -> str:
        """获取运动提示词（用于视频生成）"""
        if not self.camera_movement or self.camera_movement == CameraMovement.STATIC:
            return "static camera, no movement"
        
        motion_map = {
            "zoom_in": "camera slowly zooms in",
            "zoom_out": "camera slowly zooms out",
            "pan_left": "camera pans left",
            "pan_right": "camera pans right",
            "tilt_up": "camera tilts up",
            "tilt_down": "camera tilts down",
            "truck_left": "camera moves left",
            "truck_right": "camera moves right",
            "dolly_in": "camera dolly in",
            "dolly_out": "camera dolly out",
            "crane_up": "camera crane up",
            "crane_down": "camera crane down",
            "orbit": "camera orbits around subject",
            "follow": "camera follows subject"
        }
        
        speed_map = {
            "slow": "slowly",
            "medium": "smoothly",
            "fast": "quickly"
        }
        
        motion = motion_map.get(self.camera_movement.value, "")
        speed = speed_map.get(self.movement_speed, "smoothly")
        
        return f"{motion}, {speed}"
    
    def get_safe_motion_intensity(self) -> float:
        """
        获取安全的运动强度
        
        根据镜头类型自动降低强度，避免面部崩坏
        """
        base_intensity = self.movement_intensity or 0.5
        
        # 特写镜头需要降低运动强度
        if self.shot_type in [ShotType.EXTREME_CLOSE_UP, ShotType.CLOSE_UP]:
            return min(base_intensity, 0.3)  # 最大 0.3
        elif self.shot_type == ShotType.MEDIUM_CLOSE_UP:
            return min(base_intensity, 0.5)  # 最大 0.5
        else:
            return base_intensity  # 远景可以更大运动
    
    def get_motion_bucket_id(self) -> int:
        """计算 Motion Bucket ID"""
        safe_intensity = self.get_safe_motion_intensity()
        # 根据运动强度调整 motion_bucket_id
        motion_bucket = int(127 * safe_intensity * 2)  # 0-255
        return max(0, min(255, motion_bucket))

