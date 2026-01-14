# backend/app/api/v1/projects.py
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUserId, ProjectServiceDep, TaskServiceDep
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectGenerate,
    ProjectOut,
    ProjectDetail,
    ProjectListItem,
    GenerateResponse,
)
from app.schemas.base import BaseResponse, paginated_response
from app.models.project import ProjectStatus

router = APIRouter(prefix="/projects", tags=["项目"])


@router.post(
    "",
    response_model=BaseResponse[ProjectOut],
    status_code=status.HTTP_201_CREATED,
    summary="创建项目",
)
async def create_project(
    data: ProjectCreate,
    user_id: CurrentUserId,
    project_service: ProjectServiceDep,
):
    """
    创建新项目。
    
    - **title**: 项目标题
    - **story_text**: 故事文本（10-50000字）
    - **description**: 项目描述（可选）
    - **config**: 项目配置（可选）
    """
    project = await project_service.create(user_id, data)
    return BaseResponse(data=ProjectOut.model_validate(project))


@router.get(
    "",
    summary="获取项目列表",
)
async def list_projects(
    user_id: CurrentUserId,
    project_service: ProjectServiceDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[ProjectStatus] = None,
):
    """获取当前用户的项目列表。"""
    projects, total = await project_service.get_list(
        user_id=user_id,
        page=page,
        page_size=page_size,
        status=status,
    )
    
    items = [ProjectListItem.model_validate(p) for p in projects]
    return paginated_response(
        items=[item.model_dump() for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get(
    "/{project_id}",
    response_model=BaseResponse[ProjectDetail],
    summary="获取项目详情",
)
async def get_project(
    project_id: UUID,
    user_id: CurrentUserId,
    project_service: ProjectServiceDep,
):
    """获取项目详细信息，包含分镜和角色。"""
    project = await project_service.get_by_id(project_id, user_id)
    return BaseResponse(data=ProjectDetail.model_validate(project))


@router.put(
    "/{project_id}",
    response_model=BaseResponse[ProjectOut],
    summary="更新项目",
)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    user_id: CurrentUserId,
    project_service: ProjectServiceDep,
):
    """更新项目信息。"""
    project = await project_service.update(project_id, user_id, data)
    return BaseResponse(data=ProjectOut.model_validate(project))


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除项目",
)
async def delete_project(
    project_id: UUID,
    user_id: CurrentUserId,
    project_service: ProjectServiceDep,
):
    """删除项目（软删除）。"""
    await project_service.delete(project_id, user_id)


@router.post(
    "/{project_id}/generate",
    response_model=BaseResponse[GenerateResponse],
    summary="触发生成",
)
async def generate_project(
    project_id: UUID,
    data: ProjectGenerate,
    user_id: CurrentUserId,
    project_service: ProjectServiceDep,
    task_service: TaskServiceDep,
):
    """
    触发项目内容生成。
    
    - **steps**: 要执行的步骤 (默认全部)
        - storyboard: 生成分镜
        - image: 生成图片
        - video: 生成视频
        - compose: 合成
    - **force**: 是否强制重新生成
    """
    # 验证项目权限
    await project_service.get_by_id(project_id, user_id)
    
    # 创建生成任务
    tasks = await task_service.create_generation_tasks(
        project_id=project_id,
        steps=data.steps,
    )
    
    return BaseResponse(
        data=GenerateResponse(
            project_id=project_id,
            task_ids=[t.id for t in tasks],
            estimated_time=len(tasks) * 60,  # 预估每个任务60秒
        )
    )
