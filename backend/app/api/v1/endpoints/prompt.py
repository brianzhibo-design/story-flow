"""
提示词融合 API 端点

提供：
- 场景提示词融合
- 视频提示词融合
- 角色肖像提示词
- 一致性验证
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.visual_element import VisualElement, ElementType
from app.services.prompt_fusion import prompt_fusion_service
from app.schemas.elements import ShotAttributes, ShotType, CameraAngle, CameraMovement


router = APIRouter(prefix="/prompt", tags=["提示词融合"])


# ==================== Request Schemas ====================

class ShotAttributesSchema(BaseModel):
    """镜头属性"""
    shot_type: Optional[str] = None
    camera_angle: Optional[str] = None
    camera_movement: Optional[str] = None
    movement_speed: Optional[str] = "medium"
    movement_intensity: Optional[float] = 0.5
    depth_of_field: Optional[str] = None
    composition: Optional[str] = None


class CharacterStateSchema(BaseModel):
    """角色状态"""
    position: Optional[str] = None  # left/center/right
    action: Optional[str] = None
    expression: Optional[str] = None


class FuseSceneRequest(BaseModel):
    """融合场景提示词请求"""
    project_id: UUID
    scene_description: str
    character_ids: list[UUID] = []
    location_id: Optional[UUID] = None
    costume_ids: list[UUID] = []
    prop_ids: list[UUID] = []
    style_id: Optional[UUID] = None
    shot: Optional[ShotAttributesSchema] = None
    character_states: Optional[dict[str, CharacterStateSchema]] = None


class FuseVideoRequest(BaseModel):
    """融合视频提示词请求"""
    image_prompt: str
    shot: ShotAttributesSchema
    duration: float = Field(default=5.0, ge=1.0, le=30.0)


class CharacterPortraitRequest(BaseModel):
    """角色肖像请求"""
    character_id: UUID
    costume_id: Optional[UUID] = None
    expression: Optional[str] = None
    pose: Optional[str] = None
    style_id: Optional[UUID] = None


class ValidateConsistencyRequest(BaseModel):
    """验证一致性请求"""
    project_id: UUID
    character_ids: list[UUID]
    location_id: Optional[UUID] = None
    prop_ids: list[UUID] = []


# ==================== Response Schemas ====================

class FuseSceneResponse(BaseModel):
    """融合场景响应"""
    prompt: str
    negative_prompt: str
    warnings: list[str]
    lighting_source: Optional[str]
    generation_params: dict


class FuseVideoResponse(BaseModel):
    """融合视频响应"""
    prompt: str
    motion_prompt: str
    motion_bucket_id: int
    safe_intensity: float
    duration: float


class CharacterPortraitResponse(BaseModel):
    """角色肖像响应"""
    prompt: str
    negative_prompt: str


class ValidateConsistencyResponse(BaseModel):
    """验证一致性响应"""
    is_valid: bool
    warnings: list[str]


# ==================== Endpoints ====================

@router.post("/fuse-scene", response_model=FuseSceneResponse)
async def fuse_scene_prompt(
    request: FuseSceneRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    融合完整场景提示词
    
    基于角色、场景、道具、风格生成最终提示词
    """
    # 获取角色
    characters = []
    if request.character_ids:
        result = await db.execute(
            select(VisualElement).where(
                VisualElement.id.in_(request.character_ids),
                VisualElement.element_type == ElementType.CHARACTER
            )
        )
        characters = list(result.scalars().all())
    
    # 获取场景
    location = None
    if request.location_id:
        result = await db.execute(
            select(VisualElement).where(
                VisualElement.id == request.location_id,
                VisualElement.element_type == ElementType.LOCATION
            )
        )
        location = result.scalar_one_or_none()
    
    # 获取服装
    costumes = []
    if request.costume_ids:
        result = await db.execute(
            select(VisualElement).where(
                VisualElement.id.in_(request.costume_ids),
                VisualElement.element_type == ElementType.COSTUME
            )
        )
        costumes = list(result.scalars().all())
    
    # 获取道具
    props = []
    if request.prop_ids:
        result = await db.execute(
            select(VisualElement).where(
                VisualElement.id.in_(request.prop_ids),
                VisualElement.element_type == ElementType.PROP
            )
        )
        props = list(result.scalars().all())
    
    # 获取风格
    style = None
    if request.style_id:
        result = await db.execute(
            select(VisualElement).where(
                VisualElement.id == request.style_id,
                VisualElement.element_type == ElementType.STYLE
            )
        )
        style = result.scalar_one_or_none()
    
    # 构建镜头属性
    shot = None
    if request.shot:
        shot = ShotAttributes(
            shot_type=ShotType(request.shot.shot_type) if request.shot.shot_type else None,
            camera_angle=CameraAngle(request.shot.camera_angle) if request.shot.camera_angle else None,
            camera_movement=CameraMovement(request.shot.camera_movement) if request.shot.camera_movement else None,
            movement_speed=request.shot.movement_speed,
            movement_intensity=request.shot.movement_intensity,
            depth_of_field=request.shot.depth_of_field,
            composition=request.shot.composition
        )
    
    # 转换角色状态
    character_states = None
    if request.character_states:
        character_states = {
            k: v.model_dump() for k, v in request.character_states.items()
        }
    
    # 融合提示词
    result = prompt_fusion_service.fuse_scene_prompt(
        scene_description=request.scene_description,
        characters=characters,
        location=location,
        costumes=costumes,
        props=props,
        style=style,
        shot=shot,
        character_states=character_states
    )
    
    return FuseSceneResponse(**result)


@router.post("/fuse-video", response_model=FuseVideoResponse)
async def fuse_video_prompt(
    request: FuseVideoRequest,
    current_user: User = Depends(get_current_user)
):
    """
    融合视频生成提示词
    
    添加运动控制信息
    """
    shot = ShotAttributes(
        shot_type=ShotType(request.shot.shot_type) if request.shot.shot_type else None,
        camera_angle=CameraAngle(request.shot.camera_angle) if request.shot.camera_angle else None,
        camera_movement=CameraMovement(request.shot.camera_movement) if request.shot.camera_movement else None,
        movement_speed=request.shot.movement_speed,
        movement_intensity=request.shot.movement_intensity
    )
    
    result = prompt_fusion_service.fuse_video_prompt(
        image_prompt=request.image_prompt,
        shot=shot,
        duration=request.duration
    )
    
    return FuseVideoResponse(**result)


@router.post("/character-portrait", response_model=CharacterPortraitResponse)
async def generate_character_portrait_prompt(
    request: CharacterPortraitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成角色肖像提示词
    
    用于生成角色参考图
    """
    # 获取角色
    result = await db.execute(
        select(VisualElement).where(
            VisualElement.id == request.character_id,
            VisualElement.element_type == ElementType.CHARACTER
        )
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 获取服装
    costume = None
    if request.costume_id:
        result = await db.execute(
            select(VisualElement).where(
                VisualElement.id == request.costume_id
            )
        )
        costume = result.scalar_one_or_none()
    
    # 获取风格
    style = None
    if request.style_id:
        result = await db.execute(
            select(VisualElement).where(
                VisualElement.id == request.style_id
            )
        )
        style = result.scalar_one_or_none()
    
    result = prompt_fusion_service.fuse_character_portrait_prompt(
        character=character,
        costume=costume,
        expression=request.expression,
        pose=request.pose,
        style=style
    )
    
    return CharacterPortraitResponse(**result)


@router.post("/validate", response_model=ValidateConsistencyResponse)
async def validate_consistency(
    request: ValidateConsistencyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    验证场景一致性
    
    检查角色是否有一致性锚点、时代是否匹配等
    """
    # 获取角色
    characters = []
    if request.character_ids:
        result = await db.execute(
            select(VisualElement).where(
                VisualElement.id.in_(request.character_ids)
            )
        )
        characters = list(result.scalars().all())
    
    # 获取场景
    location = None
    if request.location_id:
        result = await db.execute(
            select(VisualElement).where(VisualElement.id == request.location_id)
        )
        location = result.scalar_one_or_none()
    
    # 获取道具
    props = []
    if request.prop_ids:
        result = await db.execute(
            select(VisualElement).where(
                VisualElement.id.in_(request.prop_ids)
            )
        )
        props = list(result.scalars().all())
    
    warnings = prompt_fusion_service.validate_scene_consistency(
        characters=characters,
        location=location,
        props=props
    )
    
    return ValidateConsistencyResponse(
        is_valid=len(warnings) == 0,
        warnings=warnings
    )

