# backend/app/schemas/base.py
from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

DataT = TypeVar("DataT")


class ResponseMeta(BaseModel):
    """响应元数据"""
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BaseResponse(BaseModel, Generic[DataT]):
    """基础响应模式"""
    code: int = 0
    message: str = "success"
    data: Optional[DataT] = None
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


class ResponseModel(BaseModel):
    """通用响应模型"""
    code: int = 0
    message: str = "success"
    data: Any = None


class ErrorDetail(BaseModel):
    """错误详情"""
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    """错误响应模式"""
    code: int
    message: str
    errors: Optional[list[ErrorDetail]] = None
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


class PaginationMeta(BaseModel):
    """分页元数据"""
    page: int = 1
    page_size: int = 20
    total: int = 0
    total_pages: int = 0


class PaginatedData(BaseModel, Generic[DataT]):
    """分页数据"""
    items: list[DataT]
    pagination: PaginationMeta


class PaginatedResponse(BaseModel, Generic[DataT]):
    """分页响应模式"""
    code: int = 0
    message: str = "success"
    data: PaginatedData[DataT]
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


# 便捷函数
def success_response(data: Any = None, message: str = "success") -> dict:
    """构建成功响应"""
    return {
        "code": 0,
        "message": message,
        "data": data,
        "meta": {
            "timestamp": datetime.utcnow().isoformat()
        }
    }


def error_response(
    code: int,
    message: str,
    errors: Optional[list[dict]] = None
) -> dict:
    """构建错误响应"""
    return {
        "code": code,
        "message": message,
        "errors": errors,
        "meta": {
            "timestamp": datetime.utcnow().isoformat()
        }
    }


def paginated_response(
    items: list,
    page: int,
    page_size: int,
    total: int
) -> dict:
    """构建分页响应"""
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages
            }
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat()
        }
    }
