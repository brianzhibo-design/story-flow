"""
Inpainting 局部修改 API 端点

提供：
- 修改文字
- 修改表情
- 修改视线
- 添加/删除元素
"""

from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.user import User
from app.services.inpainting_service import inpainting_service, InpaintRegion


router = APIRouter(prefix="/inpaint", tags=["局部修改"])


# ==================== Request Schemas ====================

class RegionSchema(BaseModel):
    """区域定义"""
    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)
    width: int = Field(..., gt=0)
    height: int = Field(..., gt=0)


class ModifyTextRequest(BaseModel):
    """修改文字请求"""
    image_url: str
    mask_url: str
    new_text: str
    text_style: str = "neon sign"
    language: Literal["english", "chinese"] = "english"


class ModifyExpressionRequest(BaseModel):
    """修改表情请求"""
    image_url: str
    mask_url: str
    target_expression: Literal[
        "smiling", "crying", "angry", "surprised",
        "neutral", "laughing", "sad", "scared", "disgusted", "confused"
    ]
    preserve_identity: Optional[str] = None  # 一致性锚点


class ModifyGazeRequest(BaseModel):
    """修改视线请求"""
    image_url: str
    mask_url: str
    gaze_direction: Literal[
        "looking_left", "looking_right", "looking_up",
        "looking_down", "looking_camera"
    ]


class AddElementsRequest(BaseModel):
    """添加元素请求"""
    image_url: str
    mask_url: str
    elements: list[str]
    scene_context: Optional[str] = None


class RemoveElementsRequest(BaseModel):
    """删除元素请求"""
    image_url: str
    mask_url: str
    fill_with: str = "background"
    context_description: Optional[str] = None


class ChangeClothingRequest(BaseModel):
    """更换服装请求"""
    image_url: str
    mask_url: str
    new_clothing_description: str
    preserve_body_pose: bool = True


class CreateMaskRequest(BaseModel):
    """创建蒙版请求"""
    image_width: int
    image_height: int
    region: RegionSchema


# ==================== Response Schemas ====================

class InpaintWorkflowResponse(BaseModel):
    """Inpaint 工作流响应"""
    workflow: dict
    message: str


class MaskResponse(BaseModel):
    """蒙版响应"""
    mask_base64: str
    message: str = "蒙版已创建"


# ==================== Endpoints ====================

@router.post("/text", response_model=InpaintWorkflowResponse)
async def modify_text_workflow(
    request: ModifyTextRequest,
    current_user: User = Depends(get_current_user)
):
    """
    获取修改文字的工作流
    
    用于替换路牌、招牌等文字
    """
    workflow = inpainting_service.modify_text_workflow(
        image_path=request.image_url,
        mask_path=request.mask_url,
        new_text=request.new_text,
        text_style=request.text_style,
        language=request.language
    )
    
    return InpaintWorkflowResponse(
        workflow=workflow,
        message=f"文字修改工作流已生成: '{request.new_text}'"
    )


@router.post("/expression", response_model=InpaintWorkflowResponse)
async def modify_expression_workflow(
    request: ModifyExpressionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    获取修改表情的工作流
    
    支持多种表情类型，可保持角色一致性
    """
    workflow = inpainting_service.modify_expression_workflow(
        image_path=request.image_url,
        mask_path=request.mask_url,
        target_expression=request.target_expression,
        preserve_identity=request.preserve_identity
    )
    
    return InpaintWorkflowResponse(
        workflow=workflow,
        message=f"表情修改工作流已生成: {request.target_expression}"
    )


@router.post("/gaze", response_model=InpaintWorkflowResponse)
async def modify_gaze_workflow(
    request: ModifyGazeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    获取修改视线方向的工作流
    """
    workflow = inpainting_service.modify_gaze_workflow(
        image_path=request.image_url,
        mask_path=request.mask_url,
        gaze_direction=request.gaze_direction
    )
    
    return InpaintWorkflowResponse(
        workflow=workflow,
        message=f"视线修改工作流已生成: {request.gaze_direction}"
    )


@router.post("/add-elements", response_model=InpaintWorkflowResponse)
async def add_elements_workflow(
    request: AddElementsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    获取添加元素的工作流
    
    在指定区域添加路人、车辆等元素
    """
    workflow = inpainting_service.add_elements_workflow(
        image_path=request.image_url,
        mask_path=request.mask_url,
        elements=request.elements,
        scene_context=request.scene_context
    )
    
    return InpaintWorkflowResponse(
        workflow=workflow,
        message=f"添加元素工作流已生成: {', '.join(request.elements)}"
    )


@router.post("/remove-elements", response_model=InpaintWorkflowResponse)
async def remove_elements_workflow(
    request: RemoveElementsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    获取删除元素的工作流
    
    去除杂物、水印等不需要的元素
    """
    workflow = inpainting_service.remove_elements_workflow(
        image_path=request.image_url,
        mask_path=request.mask_url,
        fill_with=request.fill_with,
        context_description=request.context_description
    )
    
    return InpaintWorkflowResponse(
        workflow=workflow,
        message="删除元素工作流已生成"
    )


@router.post("/change-clothing", response_model=InpaintWorkflowResponse)
async def change_clothing_workflow(
    request: ChangeClothingRequest,
    current_user: User = Depends(get_current_user)
):
    """
    获取更换服装的工作流
    """
    workflow = inpainting_service.change_clothing_workflow(
        image_path=request.image_url,
        mask_path=request.mask_url,
        new_clothing_description=request.new_clothing_description,
        preserve_body_pose=request.preserve_body_pose
    )
    
    return InpaintWorkflowResponse(
        workflow=workflow,
        message=f"服装更换工作流已生成: {request.new_clothing_description}"
    )


@router.get("/expressions")
async def list_expressions(
    current_user: User = Depends(get_current_user)
):
    """
    列出所有支持的表情类型
    """
    return {
        "expressions": list(inpainting_service.EXPRESSION_PROMPTS.keys()),
        "details": inpainting_service.EXPRESSION_PROMPTS
    }


@router.get("/gaze-directions")
async def list_gaze_directions(
    current_user: User = Depends(get_current_user)
):
    """
    列出所有支持的视线方向
    """
    return {
        "directions": list(inpainting_service.GAZE_PROMPTS.keys()),
        "details": inpainting_service.GAZE_PROMPTS
    }

