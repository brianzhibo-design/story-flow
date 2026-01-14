# backend/app/api/v1/tasks.py
from typing import Optional
from uuid import UUID

from fastapi import APIRouter

from app.api.deps import CurrentUserId, TaskServiceDep, ProjectServiceDep
from app.schemas.task import TaskOut, TaskDetail, TaskListOut
from app.schemas.base import BaseResponse
from app.models.task import TaskType, TaskStatus

router = APIRouter(prefix="/tasks", tags=["任务"])


@router.get(
    "/{task_id}",
    response_model=BaseResponse[TaskDetail],
    summary="获取任务详情",
)
async def get_task(
    task_id: UUID,
    task_service: TaskServiceDep,
):
    """获取任务详细信息，包含payload和result。"""
    task = await task_service.get_by_id(task_id)
    return BaseResponse(data=TaskDetail.model_validate(task))


@router.get(
    "/project/{project_id}",
    response_model=BaseResponse[TaskListOut],
    summary="获取项目任务列表",
)
async def list_project_tasks(
    project_id: UUID,
    user_id: CurrentUserId,
    task_service: TaskServiceDep,
    project_service: ProjectServiceDep,
    type: Optional[TaskType] = None,
    status: Optional[TaskStatus] = None,
):
    """获取指定项目的任务列表。"""
    # 验证项目权限
    await project_service.get_by_id(project_id, user_id)
    
    tasks = await task_service.get_project_tasks(
        project_id=project_id,
        task_type=type,
        status=status,
    )
    
    return BaseResponse(
        data=TaskListOut(
            tasks=[TaskOut.model_validate(t) for t in tasks],
            total=len(tasks),
        )
    )
