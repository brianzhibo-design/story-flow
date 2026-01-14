# backend/app/models/base.py
from datetime import datetime
from uuid import uuid4
from sqlalchemy import DateTime, func, String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator
import json

from app.core.database import Base


# 跨数据库兼容的 JSON 类型
class CompatibleJSON(TypeDecorator):
    """兼容 SQLite 和 PostgreSQL 的 JSON 类型"""
    impl = JSON
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return value
        return None
    
    def process_result_value(self, value, dialect):
        if value is not None:
            if isinstance(value, str):
                return json.loads(value)
            return value
        return None


# 导出 JSON 类型别名
JSONB = CompatibleJSON


class TimestampMixin:
    """时间戳混入类"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def generate_uuid() -> str:
    """生成 UUID 字符串"""
    return str(uuid4())


class UUIDMixin:
    """UUID主键混入类 (使用 String 类型兼容 SQLite)"""
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """模型基类"""
    __abstract__ = True
