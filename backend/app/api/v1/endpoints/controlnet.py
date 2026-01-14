"""
ControlNet API 端点

提供：
- OpenPose 骨架生成
- 多 ControlNet 组合
- 预设姿势库
"""

from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.user import User
from app.services.controlnet_service import controlnet_service, ControlNetType


router = APIRouter(prefix="/controlnet", tags=["ControlNet"])


# ==================== Request Schemas ====================

class ControlNetRequest(BaseModel):
    """ControlNet 请求"""
    controlnet_type: ControlNetType
    control_image_url: str
    prompt: str
    negative_prompt: str = ""
    strength: float = Field(default=0.8, ge=0.0, le=2.0)
    width: int = Field(default=1024, ge=512, le=2048)
    height: int = Field(default=576, ge=512, le=2048)
    seed: int = -1


class MultiControlNetItem(BaseModel):
    """多 ControlNet 项"""
    type: ControlNetType
    image_url: str
    strength: float = Field(default=0.8, ge=0.0, le=2.0)


class MultiControlNetRequest(BaseModel):
    """多 ControlNet 请求"""
    controlnets: list[MultiControlNetItem]
    prompt: str
    negative_prompt: str = ""
    width: int = Field(default=1024, ge=512, le=2048)
    height: int = Field(default=576, ge=512, le=2048)
    seed: int = -1


class InteractionPoseRequest(BaseModel):
    """双人互动姿势请求"""
    interaction_type: Literal["hug", "fight", "handshake", "back_to_back"]
    person1_x: float = Field(..., ge=0.0, le=1.0)
    person1_y: float = Field(..., ge=0.0, le=1.0)
    person2_x: float = Field(..., ge=0.0, le=1.0)
    person2_y: float = Field(..., ge=0.0, le=1.0)


# ==================== Response Schemas ====================

class ControlNetWorkflowResponse(BaseModel):
    """ControlNet 工作流响应"""
    workflow: dict
    message: str


class PoseResponse(BaseModel):
    """姿势响应"""
    person1: list
    person2: list
    description: str


class PresetPoseItem(BaseModel):
    """预设姿势项"""
    name: str
    description: str


# ==================== Endpoints ====================

@router.post("/workflow", response_model=ControlNetWorkflowResponse)
async def get_controlnet_workflow(
    request: ControlNetRequest,
    current_user: User = Depends(get_current_user)
):
    """
    获取 ControlNet 工作流
    
    支持 OpenPose、深度图、边缘检测等
    """
    workflow = controlnet_service.get_comfyui_controlnet_workflow(
        controlnet_type=request.controlnet_type,
        control_image_path=request.control_image_url,
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        strength=request.strength,
        width=request.width,
        height=request.height,
        seed=request.seed
    )
    
    return ControlNetWorkflowResponse(
        workflow=workflow,
        message=f"{request.controlnet_type.value} 工作流已生成"
    )


@router.post("/multi-workflow", response_model=ControlNetWorkflowResponse)
async def get_multi_controlnet_workflow(
    request: MultiControlNetRequest,
    current_user: User = Depends(get_current_user)
):
    """
    获取多 ControlNet 组合工作流
    
    同时使用多个 ControlNet（如 OpenPose + Depth）
    """
    controlnets = [
        {
            "type": cn.type,
            "image": cn.image_url,
            "strength": cn.strength
        }
        for cn in request.controlnets
    ]
    
    workflow = controlnet_service.get_multi_controlnet_workflow(
        controlnets=controlnets,
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        width=request.width,
        height=request.height,
        seed=request.seed
    )
    
    cn_names = [cn.type.value for cn in request.controlnets]
    
    return ControlNetWorkflowResponse(
        workflow=workflow,
        message=f"多 ControlNet 工作流已生成: {', '.join(cn_names)}"
    )


@router.post("/interaction-pose", response_model=PoseResponse)
async def generate_interaction_pose(
    request: InteractionPoseRequest,
    current_user: User = Depends(get_current_user)
):
    """
    生成双人互动的 OpenPose 骨架
    
    解决双人肢体穿模问题
    """
    pose_data = controlnet_service.generate_openpose_for_interaction(
        interaction_type=request.interaction_type,
        person1_position=(request.person1_x, request.person1_y),
        person2_position=(request.person2_x, request.person2_y)
    )
    
    if "error" in pose_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=pose_data["error"]
        )
    
    return PoseResponse(
        person1=pose_data["person1"],
        person2=pose_data["person2"],
        description=pose_data["description"]
    )


@router.get("/presets", response_model=list[PresetPoseItem])
async def list_preset_poses(
    current_user: User = Depends(get_current_user)
):
    """
    列出所有预设姿势
    """
    return controlnet_service.list_preset_poses()


@router.get("/types")
async def list_controlnet_types(
    current_user: User = Depends(get_current_user)
):
    """
    列出所有支持的 ControlNet 类型
    """
    return {
        "types": [
            {"value": t.value, "name": t.name}
            for t in ControlNetType
        ],
        "sdxl_supported": list(controlnet_service.MODEL_MAP_SDXL.keys())
    }

