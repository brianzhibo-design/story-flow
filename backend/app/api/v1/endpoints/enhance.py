"""
画质增强 API 端点

提供：
- 面部修复
- 手部修复
- 超分辨率
- 完整增强流程
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.user import User
from app.services.quality_enhancer import quality_enhancer, UpscaleMethod, EnhanceType


router = APIRouter(prefix="/enhance", tags=["画质增强"])


# ==================== Request Schemas ====================

class FaceFixRequest(BaseModel):
    """面部修复请求"""
    image_url: str
    prompt: str = "detailed face"
    negative_prompt: str = "blurry face"
    confidence: float = Field(default=0.5, ge=0.1, le=1.0)
    strength: float = Field(default=0.4, ge=0.1, le=1.0)


class UpscaleRequest(BaseModel):
    """超分请求"""
    image_url: str
    scale: int = Field(default=2, ge=2, le=4)
    method: UpscaleMethod = UpscaleMethod.ESRGAN_4X


class FullEnhanceRequest(BaseModel):
    """完整增强请求"""
    image_url: str
    prompt: str
    negative_prompt: str = ""
    enhance_face: bool = True
    enhance_hands: bool = True
    upscale: bool = False
    upscale_factor: float = Field(default=2.0, ge=1.0, le=4.0)


class EnhanceSettingsRequest(BaseModel):
    """获取推荐设置请求"""
    has_faces: bool = True
    has_hands: bool = True
    is_wide_shot: bool = False
    width: int = 1024
    height: int = 576


# ==================== Response Schemas ====================

class EnhanceWorkflowResponse(BaseModel):
    """增强工作流响应"""
    workflow: dict
    message: str = "工作流已生成，请提交到 ComfyUI 执行"


class EnhanceSettingsResponse(BaseModel):
    """推荐设置响应"""
    enhance_face: bool
    enhance_hands: bool
    face_strength: float
    hand_strength: float
    upscale: bool
    upscale_method: str


# ==================== Endpoints ====================

@router.post("/face", response_model=EnhanceWorkflowResponse)
async def get_face_fix_workflow(
    request: FaceFixRequest,
    current_user: User = Depends(get_current_user)
):
    """
    获取面部修复工作流
    
    返回 ComfyUI 工作流 JSON，可直接提交执行
    """
    workflow = quality_enhancer.get_face_fix_workflow(
        image_path=request.image_url,
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        confidence=request.confidence,
        strength=request.strength
    )
    
    return EnhanceWorkflowResponse(
        workflow=workflow,
        message="面部修复工作流已生成"
    )


@router.post("/upscale", response_model=EnhanceWorkflowResponse)
async def get_upscale_workflow(
    request: UpscaleRequest,
    current_user: User = Depends(get_current_user)
):
    """
    获取超分辨率工作流
    """
    workflow = quality_enhancer.get_upscale_workflow(
        image_path=request.image_url,
        scale=request.scale,
        method=request.method
    )
    
    return EnhanceWorkflowResponse(
        workflow=workflow,
        message=f"超分工作流已生成 ({request.scale}x)"
    )


@router.post("/full", response_model=EnhanceWorkflowResponse)
async def get_full_enhance_workflow(
    request: FullEnhanceRequest,
    current_user: User = Depends(get_current_user)
):
    """
    获取完整增强工作流
    
    包含面部修复、手部修复、超分辨率
    """
    workflow = quality_enhancer.get_full_enhance_workflow(
        image_path=request.image_url,
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        enhance_face=request.enhance_face,
        enhance_hands=request.enhance_hands,
        upscale=request.upscale,
        upscale_factor=request.upscale_factor
    )
    
    operations = []
    if request.enhance_face:
        operations.append("面部修复")
    if request.enhance_hands:
        operations.append("手部修复")
    if request.upscale:
        operations.append(f"{request.upscale_factor}x 超分")
    
    return EnhanceWorkflowResponse(
        workflow=workflow,
        message=f"完整增强工作流已生成: {', '.join(operations)}"
    )


@router.post("/settings", response_model=EnhanceSettingsResponse)
async def get_recommended_settings(
    request: EnhanceSettingsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    获取推荐的增强设置
    
    根据画面内容自动推荐最佳设置
    """
    settings = quality_enhancer.get_recommended_enhance_settings(
        has_faces=request.has_faces,
        has_hands=request.has_hands,
        is_wide_shot=request.is_wide_shot,
        current_resolution=(request.width, request.height)
    )
    
    return EnhanceSettingsResponse(**settings)

