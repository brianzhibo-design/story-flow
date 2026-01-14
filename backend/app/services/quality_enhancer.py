"""
画质优化服务

包含：
1. 面部修复 (Adetailer)
2. 手部修复
3. 超分辨率

基于《巨日禄 AI 短剧创作手记》实战经验优化
"""

from typing import Optional
from enum import Enum
from dataclasses import dataclass

from app.config import settings


class UpscaleMethod(str, Enum):
    """超分方法"""
    ESRGAN_4X = "RealESRGAN_x4plus"
    ESRGAN_4X_ANIME = "RealESRGAN_x4plus_anime_6B"
    SWINIR = "SwinIR_4x"
    LDSR = "LDSR"
    ULTIMATE_SD = "UltimateSDUpscale"


class EnhanceType(str, Enum):
    """增强类型"""
    FACE = "face"
    HAND = "hand"
    UPSCALE = "upscale"
    FACE_AND_HAND = "face_and_hand"
    FULL = "full"  # 全部增强


@dataclass
class EnhanceResult:
    """增强结果"""
    success: bool
    enhanced_url: Optional[str] = None
    operations: list[str] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.operations is None:
            self.operations = []


class QualityEnhancer:
    """
    画质增强服务
    
    核心功能：
    1. 检测并修复崩坏的面部
    2. 修复畸形的手部
    3. 提升分辨率同时保持细节
    """
    
    # 面部检测模型
    FACE_DETECTION_MODELS = [
        "face_yolov8n.pt",
        "face_yolov8s.pt",
        "mediapipe_face_full",
        "mediapipe_face_short"
    ]
    
    # 手部检测模型
    HAND_DETECTION_MODELS = [
        "hand_yolov8n.pt",
        "hand_yolov8s.pt"
    ]
    
    def get_adetailer_workflow(
        self,
        image_path: str,
        prompt: str,
        negative_prompt: str,
        face_confidence: float = 0.5,
        hand_confidence: float = 0.5,
        face_strength: float = 0.4,
        hand_strength: float = 0.5,
        checkpoint: str = "sd_xl_base_1.0.safetensors"
    ) -> dict:
        """
        生成 Adetailer (自动检测修复) 工作流
        
        自动检测人脸和手部，进行局部重绘
        """
        return {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint}
            },
            "2": {
                "class_type": "LoadImage",
                "inputs": {"image": image_path}
            },
            # 面部修复
            "3": {
                "class_type": "ADetailer",
                "inputs": {
                    "image": ["2", 0],
                    "model": ["1", 0],
                    "clip": ["1", 1],
                    "vae": ["1", 2],
                    "detection_model": "face_yolov8n.pt",
                    "confidence": face_confidence,
                    "prompt": f"detailed face, sharp features, {prompt}",
                    "negative_prompt": "blurry face, distorted, " + negative_prompt,
                    "strength": face_strength,
                    "mask_blur": 4,
                    "mask_dilation": 4,
                    "inpaint_only_masked": True,
                    "steps": 20,
                    "cfg": 7.0
                }
            },
            # 手部修复
            "4": {
                "class_type": "ADetailer",
                "inputs": {
                    "image": ["3", 0],
                    "model": ["1", 0],
                    "clip": ["1", 1],
                    "vae": ["1", 2],
                    "detection_model": "hand_yolov8n.pt",
                    "confidence": hand_confidence,
                    "prompt": f"detailed hands, five fingers, correct anatomy, {prompt}",
                    "negative_prompt": "bad hands, extra fingers, missing fingers, " + negative_prompt,
                    "strength": hand_strength,
                    "mask_blur": 4,
                    "mask_dilation": 8,
                    "inpaint_only_masked": True,
                    "steps": 20,
                    "cfg": 7.0
                }
            },
            "5": {
                "class_type": "SaveImage",
                "inputs": {"images": ["4", 0], "filename_prefix": "adetailer_output"}
            }
        }
    
    def get_face_fix_workflow(
        self,
        image_path: str,
        prompt: str,
        negative_prompt: str,
        confidence: float = 0.5,
        strength: float = 0.4
    ) -> dict:
        """仅面部修复工作流"""
        return {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": settings.DEFAULT_CHECKPOINT}
            },
            "2": {
                "class_type": "LoadImage",
                "inputs": {"image": image_path}
            },
            "3": {
                "class_type": "ADetailer",
                "inputs": {
                    "image": ["2", 0],
                    "model": ["1", 0],
                    "clip": ["1", 1],
                    "vae": ["1", 2],
                    "detection_model": "face_yolov8n.pt",
                    "confidence": confidence,
                    "prompt": f"detailed face, {prompt}",
                    "negative_prompt": "blurry face, " + negative_prompt,
                    "strength": strength,
                    "mask_blur": 4
                }
            },
            "4": {
                "class_type": "SaveImage",
                "inputs": {"images": ["3", 0], "filename_prefix": "face_fix_output"}
            }
        }
    
    def get_upscale_workflow(
        self,
        image_path: str,
        scale: int = 2,
        method: UpscaleMethod = UpscaleMethod.ESRGAN_4X
    ) -> dict:
        """
        生成超分辨率工作流
        
        适用于大远景画面的清晰度提升
        """
        return {
            "1": {
                "class_type": "LoadImage",
                "inputs": {"image": image_path}
            },
            "2": {
                "class_type": "UpscaleModelLoader",
                "inputs": {"model_name": f"{method.value}.pth"}
            },
            "3": {
                "class_type": "ImageUpscaleWithModel",
                "inputs": {
                    "image": ["1", 0],
                    "upscale_model": ["2", 0]
                }
            },
            # 如果需要缩放回目标大小
            "4": {
                "class_type": "ImageScaleBy",
                "inputs": {
                    "image": ["3", 0],
                    "upscale_method": "lanczos",
                    "scale_by": scale / 4.0  # ESRGAN 默认 4x，调整到目标倍数
                }
            },
            "5": {
                "class_type": "SaveImage",
                "inputs": {"images": ["4", 0], "filename_prefix": "upscaled_output"}
            }
        }
    
    def get_ultimate_sd_upscale_workflow(
        self,
        image_path: str,
        prompt: str,
        negative_prompt: str,
        tile_size: int = 512,
        denoise: float = 0.3,
        upscale_by: float = 2.0,
        checkpoint: str = "sd_xl_base_1.0.safetensors"
    ) -> dict:
        """
        Ultimate SD Upscale 工作流
        
        分块超分，增加皮肤纹理和材质细节
        适合大远景画面
        """
        return {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint}
            },
            "2": {
                "class_type": "LoadImage",
                "inputs": {"image": image_path}
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt, "clip": ["1", 1]}
            },
            "4": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": negative_prompt, "clip": ["1", 1]}
            },
            "5": {
                "class_type": "UpscaleModelLoader",
                "inputs": {"model_name": "RealESRGAN_x4plus.pth"}
            },
            "6": {
                "class_type": "UltimateSDUpscale",
                "inputs": {
                    "model": ["1", 0],
                    "positive": ["3", 0],
                    "negative": ["4", 0],
                    "vae": ["1", 2],
                    "upscale_model": ["5", 0],
                    "image": ["2", 0],
                    "upscale_by": upscale_by,
                    "seed": -1,
                    "steps": 20,
                    "cfg": 7.0,
                    "sampler_name": "euler_ancestral",
                    "scheduler": "normal",
                    "denoise": denoise,
                    "tile_width": tile_size,
                    "tile_height": tile_size,
                    "mask_blur": 8,
                    "tile_padding": 32,
                    "seam_fix_mode": "half_tile",
                    "seam_fix_denoise": denoise / 2,
                    "seam_fix_width": 64,
                    "seam_fix_mask_blur": 8,
                    "seam_fix_padding": 16,
                    "force_uniform_tiles": True
                }
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {"images": ["6", 0], "filename_prefix": "ultimate_upscale"}
            }
        }
    
    def get_full_enhance_workflow(
        self,
        image_path: str,
        prompt: str,
        negative_prompt: str,
        enhance_face: bool = True,
        enhance_hands: bool = True,
        upscale: bool = True,
        upscale_factor: float = 2.0
    ) -> dict:
        """
        完整画质增强工作流
        
        顺序：面部修复 -> 手部修复 -> 超分
        """
        workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": settings.DEFAULT_CHECKPOINT}
            },
            "2": {
                "class_type": "LoadImage",
                "inputs": {"image": image_path}
            },
        }
        
        current_image = ["2", 0]
        node_id = 3
        
        # 面部修复
        if enhance_face:
            workflow[str(node_id)] = {
                "class_type": "ADetailer",
                "inputs": {
                    "image": current_image,
                    "model": ["1", 0],
                    "clip": ["1", 1],
                    "vae": ["1", 2],
                    "detection_model": "face_yolov8n.pt",
                    "confidence": 0.5,
                    "prompt": f"detailed face, {prompt}",
                    "negative_prompt": "blurry face, " + negative_prompt,
                    "strength": 0.4,
                    "mask_blur": 4
                }
            }
            current_image = [str(node_id), 0]
            node_id += 1
        
        # 手部修复
        if enhance_hands:
            workflow[str(node_id)] = {
                "class_type": "ADetailer",
                "inputs": {
                    "image": current_image,
                    "model": ["1", 0],
                    "clip": ["1", 1],
                    "vae": ["1", 2],
                    "detection_model": "hand_yolov8n.pt",
                    "confidence": 0.5,
                    "prompt": f"detailed hands, five fingers, {prompt}",
                    "negative_prompt": "bad hands, extra fingers, " + negative_prompt,
                    "strength": 0.5,
                    "mask_blur": 4
                }
            }
            current_image = [str(node_id), 0]
            node_id += 1
        
        # 超分辨率
        if upscale:
            workflow[str(node_id)] = {
                "class_type": "UpscaleModelLoader",
                "inputs": {"model_name": "RealESRGAN_x4plus.pth"}
            }
            upscale_loader_id = node_id
            node_id += 1
            
            workflow[str(node_id)] = {
                "class_type": "ImageUpscaleWithModel",
                "inputs": {
                    "image": current_image,
                    "upscale_model": [str(upscale_loader_id), 0]
                }
            }
            current_image = [str(node_id), 0]
            node_id += 1
            
            # 调整到目标尺寸
            if upscale_factor != 4.0:
                workflow[str(node_id)] = {
                    "class_type": "ImageScaleBy",
                    "inputs": {
                        "image": current_image,
                        "upscale_method": "lanczos",
                        "scale_by": upscale_factor / 4.0
                    }
                }
                current_image = [str(node_id), 0]
                node_id += 1
        
        # 保存
        workflow[str(node_id)] = {
            "class_type": "SaveImage",
            "inputs": {"images": current_image, "filename_prefix": "enhanced_output"}
        }
        
        return workflow
    
    def should_auto_upscale(self, width: int, height: int) -> bool:
        """判断是否需要自动超分"""
        min_dim = min(width, height)
        return min_dim < getattr(settings, 'AUTO_UPSCALE_THRESHOLD', 720)
    
    def get_recommended_enhance_settings(
        self,
        has_faces: bool = True,
        has_hands: bool = True,
        is_wide_shot: bool = False,
        current_resolution: tuple[int, int] = (1024, 576)
    ) -> dict:
        """
        获取推荐的增强设置
        
        根据画面内容自动推荐
        """
        settings_dict = {
            "enhance_face": has_faces,
            "enhance_hands": has_hands,
            "face_strength": 0.3 if is_wide_shot else 0.4,
            "hand_strength": 0.4 if is_wide_shot else 0.5,
            "upscale": self.should_auto_upscale(*current_resolution),
            "upscale_method": UpscaleMethod.ESRGAN_4X.value
        }
        
        return settings_dict


# 全局实例
quality_enhancer = QualityEnhancer()

