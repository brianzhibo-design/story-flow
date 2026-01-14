"""
视觉元素 API
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.project import Project
from app.models.visual_element import VisualElement, ElementType
from app.services.element_service import ElementService
from app.services.element_extractor import ElementExtractor
from app.services.file_service import get_file_service
from app.schemas.base import ResponseModel
from app.schemas.elements import CharacterAttributes, LocationAttributes, PropAttributes, CostumeAttributes
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/elements", tags=["Elements"])


@router.get("/project/{project_id}")
async def get_project_elements(
    project_id: UUID,
    element_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """获取项目的所有视觉元素"""
    service = ElementService(db)
    
    type_enum = ElementType(element_type) if element_type else None
    elements = await service.get_project_elements(project_id, type_enum)
    
    return ResponseModel(
        code=0,
        message="success",
        data=[
            {
                "id": str(e.id),
                "type": e.type,
                "name": e.name,
                "name_en": e.name_en,
                "description": e.description,
                "prompt_en": e.prompt_en,
                "primary_reference_url": e.primary_reference_url,
                "attributes": e.attributes,
                "usage_count": e.usage_count,
                "tags": e.tags
            }
            for e in elements
        ]
    )


@router.post("/project/{project_id}/extract")
async def extract_elements(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """从项目故事中提取视觉元素"""
    
    # 获取项目
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 提取元素
    extractor = ElementExtractor()
    elements_data = await extractor.extract_all(project.story_text)
    
    service = ElementService(db)
    created = {"characters": 0, "locations": 0, "props": 0, "costumes": 0}
    
    # 创建角色
    for data in elements_data.get("characters", []):
        attrs = CharacterAttributes(**{k: v for k, v in data.items() if k in CharacterAttributes.model_fields})
        await service.create_character(
            project_id=project_id,
            name=data["name"],
            attrs=attrs,
            name_en=data.get("name_en"),
            description=data.get("description")
        )
        created["characters"] += 1
    
    # 创建场景
    for data in elements_data.get("locations", []):
        attrs = LocationAttributes(**{k: v for k, v in data.items() if k in LocationAttributes.model_fields})
        await service.create_location(
            project_id=project_id,
            name=data["name"],
            attrs=attrs,
            name_en=data.get("name_en"),
            description=data.get("description")
        )
        created["locations"] += 1
    
    # 创建道具
    for data in elements_data.get("props", []):
        attrs = PropAttributes(**{k: v for k, v in data.items() if k in PropAttributes.model_fields})
        await service.create_prop(
            project_id=project_id,
            name=data["name"],
            attrs=attrs,
            name_en=data.get("name_en"),
            description=data.get("description")
        )
        created["props"] += 1
    
    # 创建服装
    for data in elements_data.get("costumes", []):
        attrs = CostumeAttributes(**{k: v for k, v in data.items() if k in CostumeAttributes.model_fields})
        await service.create_costume(
            project_id=project_id,
            name=data["name"],
            attrs=attrs,
            description=data.get("description")
        )
        created["costumes"] += 1
    
    return ResponseModel(code=0, message="success", data=created)


@router.post("/{element_id}/reference")
async def upload_reference(
    element_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """上传元素参考图"""
    
    element = await db.get(VisualElement, element_id)
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    
    # 上传文件
    file_service = get_file_service()
    result = await file_service.upload_element_reference(
        project_id=str(element.project_id),
        element_type=element.type,
        element_id=str(element_id),
        data=await file.read()
    )
    
    # 更新元素
    element.primary_reference_url = result.url
    refs = element.reference_images or []
    if result.url not in refs:
        refs.append(result.url)
        element.reference_images = refs
    await db.commit()
    
    return ResponseModel(code=0, message="success", data={"reference_url": result.url})


@router.put("/{element_id}")
async def update_element(
    element_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """更新元素"""
    
    element = await db.get(VisualElement, element_id)
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    
    # 更新允许的字段
    allowed = ["name", "name_en", "description", "attributes", "tags", "consistency_config"]
    for key in allowed:
        if key in data:
            setattr(element, key, data[key])
    
    # 重新生成提示词
    if "attributes" in data:
        service = ElementService(db)
        element.prompt_en = service._generate_prompt(
            ElementType(element.type),
            element.attributes
        )
    
    await db.commit()
    return ResponseModel(code=0, message="success", data={"id": str(element_id)})


@router.delete("/{element_id}")
async def delete_element(
    element_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ResponseModel:
    """删除元素（软删除）"""
    
    element = await db.get(VisualElement, element_id)
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    
    element.is_active = False
    await db.commit()
    
    return ResponseModel(code=0, message="success", data=None)

