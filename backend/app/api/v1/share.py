"""
分享与协作 API

支持:
- 分享链接管理
- 协作者管理
- 评论系统
"""
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.collaboration import (
    ProjectShare, ProjectCollaborator, ProjectComment,
    ShareType, CollaboratorRole
)
from app.core.security import hash_password, verify_password

router = APIRouter(prefix="/share", tags=["分享协作"])


# ==================== 请求模型 ====================

class CreateShareRequest(BaseModel):
    """创建分享请求"""
    project_id: str = Field(..., description="项目 ID")
    share_type: str = Field(default="view", description="分享权限: view/comment/edit")
    password: Optional[str] = Field(None, description="访问密码")
    expires_days: Optional[int] = Field(None, ge=1, le=365, description="有效期天数")
    max_views: Optional[int] = Field(None, ge=1, description="最大访问次数")
    allow_download: bool = Field(default=False, description="是否允许下载")
    title: Optional[str] = Field(None, max_length=100, description="自定义标题")


class AddCollaboratorRequest(BaseModel):
    """添加协作者请求"""
    project_id: str = Field(..., description="项目 ID")
    email: str = Field(..., description="协作者邮箱")
    role: str = Field(default="viewer", description="角色: viewer/commenter/editor/admin")


class CreateCommentRequest(BaseModel):
    """创建评论请求"""
    content: str = Field(..., min_length=1, max_length=2000, description="评论内容")
    scene_id: Optional[str] = Field(None, description="分镜 ID")
    parent_id: Optional[str] = Field(None, description="父评论 ID (回复)")
    timestamp: Optional[float] = Field(None, ge=0, description="视频时间戳 (秒)")
    position_x: Optional[float] = Field(None, ge=0, le=100, description="标注 X 坐标 (%)")
    position_y: Optional[float] = Field(None, ge=0, le=100, description="标注 Y 坐标 (%)")


# ==================== 分享链接 API ====================

@router.post("/create")
async def create_share(
    request: CreateShareRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    创建分享链接
    """
    # 验证项目归属
    stmt = select(Project).where(
        and_(
            Project.id == request.project_id,
            Project.user_id == str(current_user.id)
        )
    )
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在或无权限")
    
    # 验证分享类型
    try:
        share_type = ShareType(request.share_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的分享类型")
    
    # 生成分享码
    share_code = secrets.token_urlsafe(16)[:16]
    
    # 计算过期时间
    expires_at = None
    if request.expires_days:
        expires_at = datetime.utcnow() + timedelta(days=request.expires_days)
    
    # 创建分享记录
    share = ProjectShare(
        project_id=request.project_id,
        share_code=share_code,
        share_type=share_type,
        title=request.title,
        password_hash=hash_password(request.password) if request.password else None,
        expires_at=expires_at,
        max_views=request.max_views,
        allow_download=request.allow_download,
        created_by=str(current_user.id)
    )
    
    db.add(share)
    await db.commit()
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "share_code": share_code,
            "share_url": f"https://storyflow.com/s/{share_code}",
            "share_type": share_type.value,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "has_password": bool(request.password)
        }
    }


@router.get("/access/{share_code}")
async def access_shared_project(
    share_code: str,
    password: Optional[str] = None,
    db=Depends(get_db)
):
    """
    访问分享的项目
    """
    # 查找分享记录
    stmt = (
        select(ProjectShare)
        .options(selectinload(ProjectShare.project))
        .where(ProjectShare.share_code == share_code)
    )
    result = await db.execute(stmt)
    share = result.scalar_one_or_none()
    
    if not share:
        raise HTTPException(status_code=404, detail="分享链接不存在")
    
    if not share.is_active:
        raise HTTPException(status_code=410, detail="分享链接已失效")
    
    # 检查有效期
    if share.expires_at and share.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="分享链接已过期")
    
    # 检查访问次数
    if share.max_views and share.view_count >= share.max_views:
        raise HTTPException(status_code=410, detail="分享链接访问次数已达上限")
    
    # 检查密码
    if share.password_hash:
        if not password:
            raise HTTPException(status_code=401, detail="需要密码")
        if not verify_password(password, share.password_hash):
            raise HTTPException(status_code=401, detail="密码错误")
    
    # 更新访问计数
    share.view_count += 1
    await db.commit()
    
    # 返回项目数据
    project = share.project
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "project": {
                "id": str(project.id),
                "title": share.title or project.title,
                "style": project.style,
                # 根据权限返回不同数据
            },
            "permissions": {
                "type": share.share_type.value,
                "can_view": True,
                "can_comment": share.share_type in [ShareType.COMMENT, ShareType.EDIT],
                "can_edit": share.share_type == ShareType.EDIT,
                "can_download": share.allow_download
            }
        }
    }


@router.get("/list/{project_id}")
async def list_shares(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    获取项目的所有分享链接
    """
    # 验证权限
    stmt = select(Project).where(
        and_(
            Project.id == project_id,
            Project.user_id == str(current_user.id)
        )
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="项目不存在或无权限")
    
    # 查询分享列表
    stmt = (
        select(ProjectShare)
        .where(ProjectShare.project_id == project_id)
        .order_by(ProjectShare.created_at.desc())
    )
    result = await db.execute(stmt)
    shares = result.scalars().all()
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "shares": [
                {
                    "id": str(s.id),
                    "share_code": s.share_code,
                    "share_type": s.share_type.value,
                    "title": s.title,
                    "has_password": bool(s.password_hash),
                    "expires_at": s.expires_at.isoformat() if s.expires_at else None,
                    "max_views": s.max_views,
                    "view_count": s.view_count,
                    "is_active": s.is_active,
                    "created_at": s.created_at.isoformat()
                }
                for s in shares
            ]
        }
    }


@router.delete("/{share_code}")
async def delete_share(
    share_code: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    删除分享链接
    """
    stmt = (
        select(ProjectShare)
        .where(ProjectShare.share_code == share_code)
    )
    result = await db.execute(stmt)
    share = result.scalar_one_or_none()
    
    if not share:
        raise HTTPException(status_code=404, detail="分享链接不存在")
    
    if share.created_by != str(current_user.id):
        raise HTTPException(status_code=403, detail="无权限删除")
    
    share.is_active = False
    await db.commit()
    
    return {"code": 0, "message": "分享链接已删除"}


# ==================== 协作者 API ====================

@router.post("/collaborators/add")
async def add_collaborator(
    request: AddCollaboratorRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    添加协作者
    """
    # 验证项目归属
    stmt = select(Project).where(
        and_(
            Project.id == request.project_id,
            Project.user_id == str(current_user.id)
        )
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="项目不存在或无权限")
    
    # 查找用户
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if str(target_user.id) == str(current_user.id):
        raise HTTPException(status_code=400, detail="不能添加自己为协作者")
    
    # 验证角色
    try:
        role = CollaboratorRole(request.role)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的角色")
    
    # 检查是否已存在
    stmt = select(ProjectCollaborator).where(
        and_(
            ProjectCollaborator.project_id == request.project_id,
            ProjectCollaborator.user_id == str(target_user.id)
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该用户已是协作者")
    
    # 创建协作者记录
    collaborator = ProjectCollaborator(
        project_id=request.project_id,
        user_id=str(target_user.id),
        role=role,
        invited_by=str(current_user.id),
        is_accepted=True,  # 自动接受
        accepted_at=datetime.utcnow()
    )
    
    db.add(collaborator)
    await db.commit()
    
    return {
        "code": 0,
        "message": "协作者添加成功",
        "data": {
            "collaborator_id": str(collaborator.id),
            "user_email": target_user.email,
            "role": role.value
        }
    }


@router.get("/collaborators/{project_id}")
async def list_collaborators(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    获取项目协作者列表
    """
    stmt = (
        select(ProjectCollaborator)
        .options(selectinload(ProjectCollaborator.user))
        .where(ProjectCollaborator.project_id == project_id)
    )
    result = await db.execute(stmt)
    collaborators = result.scalars().all()
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "collaborators": [
                {
                    "id": str(c.id),
                    "user": {
                        "id": str(c.user.id),
                        "username": c.user.username,
                        "email": c.user.email,
                        "avatar_url": c.user.avatar_url
                    },
                    "role": c.role.value,
                    "is_accepted": c.is_accepted,
                    "invited_at": c.invited_at.isoformat() if c.invited_at else None
                }
                for c in collaborators
            ]
        }
    }


@router.put("/collaborators/{collaborator_id}")
async def update_collaborator(
    collaborator_id: str,
    role: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    更新协作者权限
    """
    try:
        new_role = CollaboratorRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的角色")
    
    stmt = select(ProjectCollaborator).where(ProjectCollaborator.id == collaborator_id)
    result = await db.execute(stmt)
    collaborator = result.scalar_one_or_none()
    
    if not collaborator:
        raise HTTPException(status_code=404, detail="协作者不存在")
    
    collaborator.role = new_role
    await db.commit()
    
    return {"code": 0, "message": "权限更新成功"}


@router.delete("/collaborators/{collaborator_id}")
async def remove_collaborator(
    collaborator_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    移除协作者
    """
    stmt = select(ProjectCollaborator).where(ProjectCollaborator.id == collaborator_id)
    result = await db.execute(stmt)
    collaborator = result.scalar_one_or_none()
    
    if not collaborator:
        raise HTTPException(status_code=404, detail="协作者不存在")
    
    await db.delete(collaborator)
    await db.commit()
    
    return {"code": 0, "message": "协作者已移除"}


# ==================== 评论 API ====================

@router.post("/comments/{project_id}")
async def create_comment(
    project_id: str,
    request: CreateCommentRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    创建评论
    """
    comment = ProjectComment(
        project_id=project_id,
        scene_id=request.scene_id,
        user_id=str(current_user.id),
        content=request.content,
        parent_id=request.parent_id,
        timestamp=request.timestamp,
        position_x=request.position_x,
        position_y=request.position_y
    )
    
    db.add(comment)
    await db.commit()
    
    return {
        "code": 0,
        "message": "评论创建成功",
        "data": {
            "comment_id": str(comment.id)
        }
    }


@router.get("/comments/{project_id}")
async def list_comments(
    project_id: str,
    scene_id: Optional[str] = None,
    db=Depends(get_db)
):
    """
    获取评论列表
    """
    stmt = (
        select(ProjectComment)
        .options(selectinload(ProjectComment.user))
        .where(
            and_(
                ProjectComment.project_id == project_id,
                ProjectComment.is_deleted == False,
                ProjectComment.parent_id == None  # 只获取顶级评论
            )
        )
    )
    
    if scene_id:
        stmt = stmt.where(ProjectComment.scene_id == scene_id)
    
    stmt = stmt.order_by(ProjectComment.created_at.desc())
    
    result = await db.execute(stmt)
    comments = result.scalars().all()
    
    def format_comment(c):
        return {
            "id": str(c.id),
            "content": c.content,
            "user": {
                "id": str(c.user.id),
                "username": c.user.username,
                "avatar_url": c.user.avatar_url
            },
            "scene_id": c.scene_id,
            "timestamp": c.timestamp,
            "position_x": c.position_x,
            "position_y": c.position_y,
            "is_resolved": c.is_resolved,
            "created_at": c.created_at.isoformat(),
            "replies": []  # TODO: 加载回复
        }
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "comments": [format_comment(c) for c in comments]
        }
    }


@router.put("/comments/{comment_id}/resolve")
async def resolve_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    标记评论为已解决
    """
    stmt = select(ProjectComment).where(ProjectComment.id == comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    comment.is_resolved = True
    comment.resolved_at = datetime.utcnow()
    comment.resolved_by = str(current_user.id)
    await db.commit()
    
    return {"code": 0, "message": "评论已标记为已解决"}


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    删除评论 (软删除)
    """
    stmt = select(ProjectComment).where(ProjectComment.id == comment_id)
    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    if comment.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="无权限删除")
    
    comment.is_deleted = True
    await db.commit()
    
    return {"code": 0, "message": "评论已删除"}

