"""
局部修改服务 (Inpainting)

核心功能：
1. 修改文字（路牌、招牌）
2. 修改表情
3. 修改视线方向
4. 添加/删除元素

基于《巨日禄 AI 短剧创作手记》实战经验优化
"""

from typing import Optional, Literal
from dataclasses import dataclass, field
from enum import Enum

from app.config import settings


@dataclass
class InpaintRegion:
    """重绘区域"""
    x: int
    y: int
    width: int
    height: int
    
    # 或使用蒙版图路径
    mask_image: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "mask_image": self.mask_image
        }


class InpaintMode(str, Enum):
    """重绘模式"""
    FILL = "fill"           # 填充（去除元素）
    REPLACE = "replace"     # 替换
    ADD = "add"             # 添加
    MODIFY = "modify"       # 修改


@dataclass 
class InpaintRequest:
    """重绘请求"""
    image_path: str
    region: InpaintRegion
    mode: InpaintMode
    prompt: str
    negative_prompt: str = ""
    denoise: float = 0.75
    preserve_identity: Optional[str] = None  # 一致性锚点


@dataclass
class InpaintResult:
    """重绘结果"""
    success: bool
    output_path: Optional[str] = None
    error: Optional[str] = None
    operation: Optional[str] = None


class InpaintingService:
    """
    Inpainting 局部修改服务
    
    应用场景：
    1. 替换路牌文字 "Shop" -> "青丘大厦"
    2. 修改角色微表情（哭泣、大笑、惊讶）
    3. 调整人物视线方向
    4. 在空街上增加路人、车辆
    5. 去除画面中的杂物、水印
    """
    
    # 表情提示词映射
    EXPRESSION_PROMPTS = {
        "smiling": "gentle smile, warm expression, happy",
        "crying": "tears streaming down face, sad expression, tearful eyes",
        "angry": "furrowed brow, angry expression, fierce eyes",
        "surprised": "wide eyes, open mouth, shocked expression",
        "neutral": "neutral expression, calm face, relaxed",
        "laughing": "laughing out loud, big smile, joyful expression, teeth showing",
        "sad": "downcast eyes, sad expression, melancholic",
        "scared": "frightened expression, wide fearful eyes",
        "disgusted": "disgusted expression, scrunched nose",
        "confused": "confused expression, raised eyebrow"
    }
    
    # 视线方向提示词
    GAZE_PROMPTS = {
        "looking_left": "eyes looking to the left, gaze directed left",
        "looking_right": "eyes looking to the right, gaze directed right",
        "looking_up": "eyes looking upward, gaze directed up",
        "looking_down": "eyes looking downward, gaze directed down",
        "looking_camera": "eyes looking directly at camera, eye contact, looking at viewer"
    }
    
    def get_inpaint_workflow(
        self,
        image_path: str,
        mask_path: str,
        prompt: str,
        negative_prompt: str,
        denoise: float = 0.75,
        checkpoint: str = "sd_xl_base_1.0.safetensors",
        steps: int = 30,
        cfg: float = 7.0
    ) -> dict:
        """
        基础 Inpainting 工作流
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
                "class_type": "LoadImage",
                "inputs": {"image": mask_path}
            },
            "4": {
                "class_type": "ImageToMask",
                "inputs": {"image": ["3", 0], "channel": "red"}
            },
            "5": {
                "class_type": "GrowMask",
                "inputs": {"mask": ["4", 0], "expand": 6, "tapered_corners": True}
            },
            "6": {
                "class_type": "VAEEncodeForInpaint",
                "inputs": {
                    "pixels": ["2", 0],
                    "vae": ["1", 2],
                    "mask": ["5", 0],
                    "grow_mask_by": 6
                }
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt, "clip": ["1", 1]}
            },
            "8": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": negative_prompt, "clip": ["1", 1]}
            },
            "9": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["1", 0],
                    "positive": ["7", 0],
                    "negative": ["8", 0],
                    "latent_image": ["6", 0],
                    "seed": -1,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler_ancestral",
                    "scheduler": "normal",
                    "denoise": denoise
                }
            },
            "10": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["9", 0], "vae": ["1", 2]}
            },
            "11": {
                "class_type": "ImageCompositeMasked",
                "inputs": {
                    "destination": ["2", 0],
                    "source": ["10", 0],
                    "mask": ["5", 0],
                    "x": 0,
                    "y": 0,
                    "resize_source": False
                }
            },
            "12": {
                "class_type": "SaveImage",
                "inputs": {"images": ["11", 0], "filename_prefix": "inpaint_output"}
            }
        }
    
    # ==================== 常用修改场景 ====================
    
    def modify_text_workflow(
        self,
        image_path: str,
        mask_path: str,
        new_text: str,
        text_style: str = "neon sign",
        language: str = "english"
    ) -> dict:
        """
        修改图片中的文字
        
        示例：将路牌 "Shop" 改为 "青丘大厦"
        """
        # 根据语言调整提示词
        if language == "chinese":
            prompt = f'Chinese characters "{new_text}", {text_style}, clear readable text, high quality typography'
        else:
            prompt = f'"{new_text}", {text_style}, clear readable text, high quality typography'
        
        negative = "blurry text, illegible, distorted, misspelled, wrong characters"
        
        return self.get_inpaint_workflow(
            image_path=image_path,
            mask_path=mask_path,
            prompt=prompt,
            negative_prompt=negative,
            denoise=0.85
        )
    
    def modify_expression_workflow(
        self,
        image_path: str,
        mask_path: str,
        target_expression: Literal[
            "smiling", "crying", "angry", "surprised", 
            "neutral", "laughing", "sad", "scared", "disgusted", "confused"
        ],
        preserve_identity: Optional[str] = None
    ) -> dict:
        """
        修改角色表情
        
        保持角色一致性的同时修改表情
        """
        base_prompt = self.EXPRESSION_PROMPTS.get(target_expression, "neutral expression")
        
        if preserve_identity:
            prompt = f"{preserve_identity}, {base_prompt}, detailed face, same person"
        else:
            prompt = f"{base_prompt}, detailed face, same person, consistent identity"
        
        negative = "different person, changed identity, blurry face, distorted features"
        
        return self.get_inpaint_workflow(
            image_path=image_path,
            mask_path=mask_path,
            prompt=prompt,
            negative_prompt=negative,
            denoise=0.65  # 较低的去噪保持更多原始特征
        )
    
    def modify_gaze_workflow(
        self,
        image_path: str,
        mask_path: str,
        gaze_direction: Literal[
            "looking_left", "looking_right", "looking_up", 
            "looking_down", "looking_camera"
        ]
    ) -> dict:
        """
        修改视线方向
        """
        gaze_prompt = self.GAZE_PROMPTS.get(gaze_direction, "")
        prompt = f"detailed eyes, {gaze_prompt}, natural eye movement"
        negative = "crossed eyes, unfocused, blurry eyes, different eye colors"
        
        return self.get_inpaint_workflow(
            image_path=image_path,
            mask_path=mask_path,
            prompt=prompt,
            negative_prompt=negative,
            denoise=0.5  # 眼睛需要更低的去噪
        )
    
    def add_elements_workflow(
        self,
        image_path: str,
        mask_path: str,
        elements: list[str],
        scene_context: Optional[str] = None
    ) -> dict:
        """
        在指定区域添加元素
        
        示例：在空街上增加路人、车辆
        """
        elements_str = ", ".join(elements)
        
        if scene_context:
            prompt = f"{elements_str}, {scene_context}, natural placement, realistic, seamless integration"
        else:
            prompt = f"{elements_str}, natural placement, realistic, seamless integration"
        
        negative = "floating, unnatural, pasted on, obvious edit, mismatched lighting"
        
        return self.get_inpaint_workflow(
            image_path=image_path,
            mask_path=mask_path,
            prompt=prompt,
            negative_prompt=negative,
            denoise=0.9  # 添加新元素需要较高去噪
        )
    
    def remove_elements_workflow(
        self,
        image_path: str,
        mask_path: str,
        fill_with: str = "background",
        context_description: Optional[str] = None
    ) -> dict:
        """
        移除画面中的元素
        
        示例：去除穿帮的杂物、水印
        """
        if context_description:
            prompt = f"clean {fill_with}, {context_description}, seamless, natural continuation"
        else:
            prompt = f"clean {fill_with}, seamless, natural, empty space"
        
        negative = "object, artifact, text, watermark, logo, person, any visible element"
        
        return self.get_inpaint_workflow(
            image_path=image_path,
            mask_path=mask_path,
            prompt=prompt,
            negative_prompt=negative,
            denoise=0.95  # 完全移除需要高去噪
        )
    
    def fix_artifact_workflow(
        self,
        image_path: str,
        mask_path: str,
        surrounding_context: str
    ) -> dict:
        """
        修复画面中的瑕疵/伪影
        """
        prompt = f"clean, natural, {surrounding_context}, seamless blend, no artifacts"
        negative = "artifact, glitch, distortion, noise, blur"
        
        return self.get_inpaint_workflow(
            image_path=image_path,
            mask_path=mask_path,
            prompt=prompt,
            negative_prompt=negative,
            denoise=0.6
        )
    
    def change_clothing_workflow(
        self,
        image_path: str,
        mask_path: str,
        new_clothing_description: str,
        preserve_body_pose: bool = True
    ) -> dict:
        """
        更换角色服装
        """
        prompt = f"wearing {new_clothing_description}, detailed clothing, realistic fabric"
        
        if preserve_body_pose:
            prompt += ", same body pose, consistent anatomy"
        
        negative = "distorted body, wrong anatomy, floating clothes"
        
        return self.get_inpaint_workflow(
            image_path=image_path,
            mask_path=mask_path,
            prompt=prompt,
            negative_prompt=negative,
            denoise=0.75
        )
    
    def change_hair_workflow(
        self,
        image_path: str,
        mask_path: str,
        new_hair_description: str,
        preserve_face: bool = True
    ) -> dict:
        """
        更换发型
        """
        prompt = f"{new_hair_description} hair, detailed hair strands, realistic"
        
        if preserve_face:
            prompt += ", same face, consistent identity"
        
        negative = "bald, wrong hair, distorted face, changed identity"
        
        return self.get_inpaint_workflow(
            image_path=image_path,
            mask_path=mask_path,
            prompt=prompt,
            negative_prompt=negative,
            denoise=0.7
        )
    
    def create_region_mask(
        self,
        image_width: int,
        image_height: int,
        region: InpaintRegion
    ) -> bytes:
        """
        创建区域蒙版图
        
        返回 PNG 格式的蒙版图像字节
        """
        try:
            from PIL import Image
            import io
            
            # 创建黑色背景
            mask = Image.new('RGB', (image_width, image_height), color='black')
            
            # 在指定区域填充白色
            from PIL import ImageDraw
            draw = ImageDraw.Draw(mask)
            draw.rectangle(
                [region.x, region.y, region.x + region.width, region.y + region.height],
                fill='white'
            )
            
            # 转换为字节
            buffer = io.BytesIO()
            mask.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except ImportError:
            raise ImportError("PIL is required for mask creation. Install with: pip install Pillow")


# 全局实例
inpainting_service = InpaintingService()

