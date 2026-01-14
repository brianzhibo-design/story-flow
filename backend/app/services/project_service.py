# backend/app/services/project_service.py
from uuid import UUID
from typing import Optional, Union

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project, ProjectStatus
from app.models.scene import Scene
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.core.exceptions import ProjectNotFoundError, ProjectAccessDeniedError


class ProjectService:
    """项目服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, user_id: Union[str, UUID], data: ProjectCreate) -> Project:
        """
        创建项目。
        
        Args:
            user_id: 用户ID
            data: 创建数据
            
        Returns:
            创建的项目
        """
        project = Project(
            user_id=str(user_id),
            title=data.title,
            description=data.description,
            story_text=data.story_text,
            config=data.config or {},
        )
        
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        
        return project
    
    async def get_by_id(
        self,
        project_id: UUID,
        user_id: Optional[Union[str, UUID]] = None,
    ) -> Project:
        """
        通过ID获取项目。
        
        Args:
            project_id: 项目ID
            user_id: 用户ID（用于权限检查）
            
        Returns:
            项目对象
            
        Raises:
            ProjectNotFoundError: 项目不存在
            ProjectAccessDeniedError: 无权访问
        """
        result = await self.db.execute(
            select(Project)
            .options(
                selectinload(Project.scenes),
                selectinload(Project.characters),
            )
            .where(
                and_(
                    Project.id == project_id,
                    Project.deleted_at.is_(None),
                )
            )
        )
        project = result.scalar_one_or_none()
        
        if not project:
            raise ProjectNotFoundError()
        
        if user_id and project.user_id != str(user_id):
            raise ProjectAccessDeniedError()
        
        return project
    
    async def get_list(
        self,
        user_id: Union[str, UUID],
        page: int = 1,
        page_size: int = 20,
        status: Optional[ProjectStatus] = None,
    ) -> tuple[list[Project], int]:
        """
        获取项目列表。
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            status: 状态筛选
            
        Returns:
            (项目列表, 总数)
        """
        # 基础查询条件
        conditions = [
            Project.user_id == str(user_id),
            Project.deleted_at.is_(None),
        ]
        
        if status:
            conditions.append(Project.status == status)
        
        # 查询总数
        count_query = select(func.count(Project.id)).where(and_(*conditions))
        total = await self.db.scalar(count_query) or 0
        
        # 查询列表
        offset = (page - 1) * page_size
        list_query = (
            select(Project)
            .where(and_(*conditions))
            .order_by(Project.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        
        result = await self.db.execute(list_query)
        projects = list(result.scalars().all())
        
        return projects, total
    
    async def update(
        self,
        project_id: UUID,
        user_id: Union[str, UUID],
        data: ProjectUpdate,
    ) -> Project:
        """
        更新项目。
        
        Args:
            project_id: 项目ID
            user_id: 用户ID
            data: 更新数据
            
        Returns:
            更新后的项目
        """
        project = await self.get_by_id(project_id, user_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        await self.db.commit()
        await self.db.refresh(project)
        
        return project
    
    async def delete(self, project_id: UUID, user_id: Union[str, UUID]) -> None:
        """
        删除项目（软删除）。
        
        Args:
            project_id: 项目ID
            user_id: 用户ID
        """
        from datetime import datetime
        
        project = await self.get_by_id(project_id, user_id)
        project.deleted_at = datetime.utcnow()
        await self.db.commit()
    
    async def update_status(
        self,
        project_id: UUID,
        status: ProjectStatus,
    ) -> Project:
        """
        更新项目状态。
        
        Args:
            project_id: 项目ID
            status: 新状态
            
        Returns:
            更新后的项目
        """
        project = await self.get_by_id(project_id)
        project.status = status
        await self.db.commit()
        await self.db.refresh(project)
        return project
    
    async def update_scene_count(self, project_id: UUID) -> None:
        """更新项目的分镜计数"""
        count = await self.db.scalar(
            select(func.count(Scene.id)).where(Scene.project_id == project_id)
        )
        
        project = await self.get_by_id(project_id)
        project.scene_count = count or 0
        await self.db.commit()
