# backend/app/models/asset.py
from typing import Optional, TYPE_CHECKING
import enum

from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum
from app.models.base import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project


class AssetType(str, enum.Enum):
    """素材类型"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    OTHER = "other"


class Asset(BaseModel):
    """素材模型"""
    
    __tablename__ = "assets"
    
    # 归属
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    project_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # 基本信息
    type: Mapped[AssetType] = mapped_column(
        SQLEnum(AssetType),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    
    # 存储
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="存储路径",
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="文件大小（字节）",
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    
    # 元数据
    metadata_: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        comment="额外元数据",
    )
    
    def __repr__(self) -> str:
        return f"<Asset {self.name}>"
