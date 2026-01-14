"""
ControlNet 服务

支持 OpenPose 骨架控制、深度图、线稿等

核心用途：
1. OpenPose - 双人互动（拥抱、打斗）必须使用
2. Depth - 保持透视关系
3. Inpaint - 局部修改（表情、文字）
"""

from typing import Optional, Literal
from dataclasses import dataclass, field
from enum import Enum
import json


class ControlNetType(str, Enum):
    """ControlNet 类型"""
    OPENPOSE = "openpose"       # 骨架姿势
    DEPTH = "depth"             # 深度图
    CANNY = "canny"             # 边缘检测
    LINEART = "lineart"         # 线稿
    SOFTEDGE = "softedge"       # 柔边
    SCRIBBLE = "scribble"       # 涂鸦
    SEGMENTATION = "segmentation"  # 语义分割
    INPAINT = "inpaint"         # 局部重绘
    TILE = "tile"               # 分块（超分用）


@dataclass
class PoseKeypoint:
    """姿势关键点 - OpenPose 格式"""
    # 18 个关键点坐标 (x, y, confidence)
    nose: tuple[float, float, float] = (0.5, 0.2, 1.0)
    neck: tuple[float, float, float] = (0.5, 0.3, 1.0)
    right_shoulder: tuple[float, float, float] = (0.4, 0.3, 1.0)
    right_elbow: tuple[float, float, float] = (0.35, 0.45, 1.0)
    right_wrist: tuple[float, float, float] = (0.3, 0.6, 1.0)
    left_shoulder: tuple[float, float, float] = (0.6, 0.3, 1.0)
    left_elbow: tuple[float, float, float] = (0.65, 0.45, 1.0)
    left_wrist: tuple[float, float, float] = (0.7, 0.6, 1.0)
    right_hip: tuple[float, float, float] = (0.45, 0.55, 1.0)
    right_knee: tuple[float, float, float] = (0.45, 0.75, 1.0)
    right_ankle: tuple[float, float, float] = (0.45, 0.95, 1.0)
    left_hip: tuple[float, float, float] = (0.55, 0.55, 1.0)
    left_knee: tuple[float, float, float] = (0.55, 0.75, 1.0)
    left_ankle: tuple[float, float, float] = (0.55, 0.95, 1.0)
    right_eye: tuple[float, float, float] = (0.45, 0.15, 1.0)
    left_eye: tuple[float, float, float] = (0.55, 0.15, 1.0)
    right_ear: tuple[float, float, float] = (0.4, 0.18, 1.0)
    left_ear: tuple[float, float, float] = (0.6, 0.18, 1.0)
    
    def to_openpose_format(self) -> list[list[float]]:
        """转换为 OpenPose JSON 格式"""
        keypoints = [
            list(self.nose),
            list(self.neck),
            list(self.right_shoulder),
            list(self.right_elbow),
            list(self.right_wrist),
            list(self.left_shoulder),
            list(self.left_elbow),
            list(self.left_wrist),
            list(self.right_hip),
            list(self.right_knee),
            list(self.right_ankle),
            list(self.left_hip),
            list(self.left_knee),
            list(self.left_ankle),
            list(self.right_eye),
            list(self.left_eye),
            list(self.right_ear),
            list(self.left_ear),
        ]
        return keypoints


@dataclass
class PresetPose:
    """预设姿势"""
    name: str
    description: str
    keypoints: PoseKeypoint
    is_multi_person: bool = False
    person_count: int = 1


class ControlNetService:
    """
    ControlNet 服务
    
    核心用途：
    1. OpenPose - 双人互动（拥抱、打斗）必须使用
    2. Depth - 保持透视关系
    3. Inpaint - 局部修改（表情、文字）
    """
    
    # ControlNet 模型映射
    MODEL_MAP = {
        ControlNetType.OPENPOSE: "control_v11p_sd15_openpose",
        ControlNetType.DEPTH: "control_v11f1p_sd15_depth",
        ControlNetType.CANNY: "control_v11p_sd15_canny",
        ControlNetType.LINEART: "control_v11p_sd15_lineart",
        ControlNetType.SOFTEDGE: "control_v11p_sd15_softedge",
        ControlNetType.SCRIBBLE: "control_v11p_sd15_scribble",
        ControlNetType.INPAINT: "control_v11p_sd15_inpaint",
        ControlNetType.TILE: "control_v11f1e_sd15_tile",
    }
    
    # SDXL ControlNet 模型
    MODEL_MAP_SDXL = {
        ControlNetType.OPENPOSE: "controlnet-openpose-sdxl-1.0",
        ControlNetType.DEPTH: "controlnet-depth-sdxl-1.0",
        ControlNetType.CANNY: "controlnet-canny-sdxl-1.0",
    }
    
    # 预设姿势库
    PRESET_POSES: dict[str, PresetPose] = {}
    
    def __init__(self):
        self._init_preset_poses()
    
    def _init_preset_poses(self):
        """初始化预设姿势库"""
        # 站立中性姿势
        self.PRESET_POSES["standing_neutral"] = PresetPose(
            name="standing_neutral",
            description="站立中性姿势",
            keypoints=PoseKeypoint()  # 使用默认值
        )
        
        # 行走姿势
        self.PRESET_POSES["walking"] = PresetPose(
            name="walking",
            description="行走姿势",
            keypoints=PoseKeypoint(
                right_shoulder=(0.38, 0.3, 1.0),
                left_shoulder=(0.62, 0.3, 1.0),
                right_hip=(0.43, 0.55, 1.0),
                left_hip=(0.57, 0.55, 1.0),
                right_knee=(0.4, 0.72, 1.0),
                left_knee=(0.6, 0.78, 1.0),
                right_ankle=(0.38, 0.92, 1.0),
                left_ankle=(0.62, 0.98, 1.0),
            )
        )
        
        # 坐姿
        self.PRESET_POSES["sitting"] = PresetPose(
            name="sitting",
            description="坐姿",
            keypoints=PoseKeypoint(
                neck=(0.5, 0.35, 1.0),
                right_hip=(0.45, 0.6, 1.0),
                left_hip=(0.55, 0.6, 1.0),
                right_knee=(0.4, 0.7, 1.0),
                left_knee=(0.6, 0.7, 1.0),
                right_ankle=(0.38, 0.85, 1.0),
                left_ankle=(0.62, 0.85, 1.0),
            )
        )
    
    def get_controlnet_model(
        self,
        controlnet_type: ControlNetType,
        is_sdxl: bool = True
    ) -> str:
        """获取 ControlNet 模型名称"""
        if is_sdxl and controlnet_type in self.MODEL_MAP_SDXL:
            return self.MODEL_MAP_SDXL[controlnet_type]
        return self.MODEL_MAP.get(controlnet_type, "")
    
    def get_comfyui_controlnet_workflow(
        self,
        controlnet_type: ControlNetType,
        control_image_path: str,
        prompt: str,
        negative_prompt: str,
        strength: float = 0.8,
        checkpoint: str = "sd_xl_base_1.0.safetensors",
        width: int = 1024,
        height: int = 576,
        seed: int = -1,
        steps: int = 30,
        cfg: float = 7.0
    ) -> dict:
        """
        生成 ComfyUI ControlNet 工作流
        """
        controlnet_model = self.get_controlnet_model(controlnet_type, is_sdxl=True)
        
        workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint}
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt, "clip": ["1", 1]}
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": negative_prompt, "clip": ["1", 1]}
            },
            "4": {
                "class_type": "ControlNetLoader",
                "inputs": {"control_net_name": f"{controlnet_model}.safetensors"}
            },
            "5": {
                "class_type": "LoadImage",
                "inputs": {"image": control_image_path}
            },
            "6": {
                "class_type": "ControlNetApplyAdvanced",
                "inputs": {
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "control_net": ["4", 0],
                    "image": ["5", 0],
                    "strength": strength,
                    "start_percent": 0.0,
                    "end_percent": 1.0
                }
            },
            "7": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                }
            },
            "8": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["1", 0],
                    "positive": ["6", 0],
                    "negative": ["6", 1],
                    "latent_image": ["7", 0],
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler_ancestral",
                    "scheduler": "normal",
                    "denoise": 1
                }
            },
            "9": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["8", 0], "vae": ["1", 2]}
            },
            "10": {
                "class_type": "SaveImage",
                "inputs": {"images": ["9", 0], "filename_prefix": "controlnet_output"}
            }
        }
        
        return workflow
    
    def get_multi_controlnet_workflow(
        self,
        controlnets: list[dict],
        prompt: str,
        negative_prompt: str,
        checkpoint: str = "sd_xl_base_1.0.safetensors",
        width: int = 1024,
        height: int = 576,
        seed: int = -1
    ) -> dict:
        """
        生成多 ControlNet 组合工作流
        
        Args:
            controlnets: [
                {"type": ControlNetType.OPENPOSE, "image": "pose.png", "strength": 0.8},
                {"type": ControlNetType.DEPTH, "image": "depth.png", "strength": 0.5}
            ]
        """
        workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint}
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt, "clip": ["1", 1]}
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": negative_prompt, "clip": ["1", 1]}
            },
        }
        
        node_id = 4
        prev_positive = ["2", 0]
        prev_negative = ["3", 0]
        
        # 链式添加 ControlNet
        for cn in controlnets:
            cn_type = cn["type"]
            cn_image = cn["image"]
            cn_strength = cn.get("strength", 0.8)
            
            model_name = self.get_controlnet_model(cn_type)
            
            # 加载 ControlNet
            workflow[str(node_id)] = {
                "class_type": "ControlNetLoader",
                "inputs": {"control_net_name": f"{model_name}.safetensors"}
            }
            cn_loader_id = node_id
            node_id += 1
            
            # 加载控制图
            workflow[str(node_id)] = {
                "class_type": "LoadImage",
                "inputs": {"image": cn_image}
            }
            img_loader_id = node_id
            node_id += 1
            
            # 应用 ControlNet
            workflow[str(node_id)] = {
                "class_type": "ControlNetApplyAdvanced",
                "inputs": {
                    "positive": prev_positive,
                    "negative": prev_negative,
                    "control_net": [str(cn_loader_id), 0],
                    "image": [str(img_loader_id), 0],
                    "strength": cn_strength,
                    "start_percent": 0.0,
                    "end_percent": 1.0
                }
            }
            prev_positive = [str(node_id), 0]
            prev_negative = [str(node_id), 1]
            node_id += 1
        
        # 添加采样节点
        workflow[str(node_id)] = {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1}
        }
        latent_id = node_id
        node_id += 1
        
        workflow[str(node_id)] = {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": prev_positive,
                "negative": prev_negative,
                "latent_image": [str(latent_id), 0],
                "seed": seed,
                "steps": 30,
                "cfg": 7,
                "sampler_name": "euler_ancestral",
                "scheduler": "normal",
                "denoise": 1
            }
        }
        sampler_id = node_id
        node_id += 1
        
        workflow[str(node_id)] = {
            "class_type": "VAEDecode",
            "inputs": {"samples": [str(sampler_id), 0], "vae": ["1", 2]}
        }
        decode_id = node_id
        node_id += 1
        
        workflow[str(node_id)] = {
            "class_type": "SaveImage",
            "inputs": {"images": [str(decode_id), 0], "filename_prefix": "multi_cn_output"}
        }
        
        return workflow
    
    def generate_openpose_for_interaction(
        self,
        interaction_type: Literal["hug", "fight", "handshake", "back_to_back"],
        person1_position: tuple[float, float],  # 画面中位置 (0-1, 0-1)
        person2_position: tuple[float, float]
    ) -> dict:
        """
        生成双人互动的 OpenPose 骨架
        
        这是解决双人肢体穿模的关键
        """
        generators = {
            "hug": self._generate_hug_pose,
            "fight": self._generate_fight_pose,
            "handshake": self._generate_handshake_pose,
            "back_to_back": self._generate_back_to_back_pose
        }
        
        generator = generators.get(interaction_type)
        if generator:
            return generator(person1_position, person2_position)
        
        return {"error": f"Unknown interaction type: {interaction_type}"}
    
    def _generate_hug_pose(
        self,
        p1_pos: tuple[float, float],
        p2_pos: tuple[float, float]
    ) -> dict:
        """生成拥抱姿势骨架"""
        # 两人面对面，手臂交叉环抱
        p1_x, p1_y = p1_pos
        p2_x, p2_y = p2_pos
        
        person1 = PoseKeypoint(
            nose=(p1_x, p1_y - 0.1, 1.0),
            neck=(p1_x, p1_y, 1.0),
            right_shoulder=(p1_x - 0.05, p1_y + 0.02, 1.0),
            left_shoulder=(p1_x + 0.05, p1_y + 0.02, 1.0),
            # 手臂环抱向对方
            right_wrist=(p2_x + 0.05, p2_y + 0.1, 1.0),
            left_wrist=(p2_x - 0.05, p2_y + 0.1, 1.0),
        )
        
        person2 = PoseKeypoint(
            nose=(p2_x, p2_y - 0.1, 1.0),
            neck=(p2_x, p2_y, 1.0),
            right_shoulder=(p2_x - 0.05, p2_y + 0.02, 1.0),
            left_shoulder=(p2_x + 0.05, p2_y + 0.02, 1.0),
            # 手臂环抱向对方
            right_wrist=(p1_x + 0.05, p1_y + 0.1, 1.0),
            left_wrist=(p1_x - 0.05, p1_y + 0.1, 1.0),
        )
        
        return {
            "person1": person1.to_openpose_format(),
            "person2": person2.to_openpose_format(),
            "description": "Two people hugging, facing each other"
        }
    
    def _generate_fight_pose(
        self,
        p1_pos: tuple[float, float],
        p2_pos: tuple[float, float]
    ) -> dict:
        """生成打斗姿势骨架"""
        p1_x, p1_y = p1_pos
        p2_x, p2_y = p2_pos
        
        # 人物1 出拳
        person1 = PoseKeypoint(
            nose=(p1_x, p1_y - 0.1, 1.0),
            neck=(p1_x, p1_y, 1.0),
            right_shoulder=(p1_x - 0.06, p1_y + 0.02, 1.0),
            left_shoulder=(p1_x + 0.06, p1_y + 0.02, 1.0),
            # 右手出拳
            right_elbow=(p1_x + 0.1, p1_y + 0.05, 1.0),
            right_wrist=(p2_x - 0.1, p2_y, 1.0),  # 拳头接近对方
            # 左手防御
            left_elbow=(p1_x + 0.02, p1_y + 0.1, 1.0),
            left_wrist=(p1_x + 0.05, p1_y + 0.05, 1.0),
        )
        
        # 人物2 防御
        person2 = PoseKeypoint(
            nose=(p2_x, p2_y - 0.1, 1.0),
            neck=(p2_x, p2_y, 1.0),
            right_shoulder=(p2_x - 0.06, p2_y + 0.02, 1.0),
            left_shoulder=(p2_x + 0.06, p2_y + 0.02, 1.0),
            # 双手防御
            right_elbow=(p2_x - 0.08, p2_y + 0.08, 1.0),
            right_wrist=(p2_x - 0.1, p2_y - 0.02, 1.0),
            left_elbow=(p2_x + 0.02, p2_y + 0.08, 1.0),
            left_wrist=(p2_x, p2_y - 0.02, 1.0),
        )
        
        return {
            "person1": person1.to_openpose_format(),
            "person2": person2.to_openpose_format(),
            "description": "Person 1 punching, Person 2 defending"
        }
    
    def _generate_handshake_pose(
        self,
        p1_pos: tuple[float, float],
        p2_pos: tuple[float, float]
    ) -> dict:
        """生成握手姿势骨架"""
        p1_x, p1_y = p1_pos
        p2_x, p2_y = p2_pos
        mid_x = (p1_x + p2_x) / 2
        mid_y = (p1_y + p2_y) / 2
        
        person1 = PoseKeypoint(
            nose=(p1_x, p1_y - 0.1, 1.0),
            neck=(p1_x, p1_y, 1.0),
            # 右手伸出握手
            right_elbow=(p1_x + 0.08, p1_y + 0.1, 1.0),
            right_wrist=(mid_x, mid_y + 0.1, 1.0),
        )
        
        person2 = PoseKeypoint(
            nose=(p2_x, p2_y - 0.1, 1.0),
            neck=(p2_x, p2_y, 1.0),
            # 右手伸出握手
            right_elbow=(p2_x - 0.08, p2_y + 0.1, 1.0),
            right_wrist=(mid_x, mid_y + 0.1, 1.0),
        )
        
        return {
            "person1": person1.to_openpose_format(),
            "person2": person2.to_openpose_format(),
            "description": "Two people shaking hands"
        }
    
    def _generate_back_to_back_pose(
        self,
        p1_pos: tuple[float, float],
        p2_pos: tuple[float, float]
    ) -> dict:
        """生成背对背站立姿势"""
        p1_x, p1_y = p1_pos
        p2_x, p2_y = p2_pos
        
        person1 = PoseKeypoint(
            nose=(p1_x - 0.05, p1_y - 0.1, 1.0),  # 面向左
            neck=(p1_x, p1_y, 1.0),
        )
        
        person2 = PoseKeypoint(
            nose=(p2_x + 0.05, p2_y - 0.1, 1.0),  # 面向右
            neck=(p2_x, p2_y, 1.0),
        )
        
        return {
            "person1": person1.to_openpose_format(),
            "person2": person2.to_openpose_format(),
            "description": "Two people standing back to back"
        }
    
    def get_preset_pose(self, pose_name: str) -> Optional[PresetPose]:
        """获取预设姿势"""
        return self.PRESET_POSES.get(pose_name)
    
    def list_preset_poses(self) -> list[dict]:
        """列出所有预设姿势"""
        return [
            {"name": p.name, "description": p.description}
            for p in self.PRESET_POSES.values()
        ]


# 全局实例
controlnet_service = ControlNetService()

