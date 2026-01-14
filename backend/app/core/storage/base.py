"""
存储后端抽象基类
"""

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from dataclasses import dataclass


@dataclass
class UploadResult:
    """上传结果"""
    path: str
    url: str
    size: int
    content_type: str
    etag: Optional[str] = None


@dataclass
class FileInfo:
    """文件信息"""
    path: str
    size: int
    content_type: str
    last_modified: str
    url: str


class StorageBackend(ABC):
    """存储后端抽象基类"""
    
    @abstractmethod
    async def upload(
        self,
        data: bytes | BinaryIO,
        path: str,
        content_type: str = "application/octet-stream",
        metadata: dict = None
    ) -> UploadResult:
        """上传文件"""
        pass
    
    @abstractmethod
    async def upload_from_url(
        self,
        source_url: str,
        target_path: str
    ) -> UploadResult:
        """从 URL 下载并上传"""
        pass
    
    @abstractmethod
    async def download(self, path: str) -> bytes:
        """下载文件"""
        pass
    
    @abstractmethod
    async def delete(self, path: str) -> bool:
        """删除文件"""
        pass
    
    @abstractmethod
    async def exists(self, path: str) -> bool:
        """检查文件是否存在"""
        pass
    
    @abstractmethod
    def get_url(self, path: str, expires: int = 3600) -> str:
        """获取访问 URL"""
        pass
    
    @abstractmethod
    async def list_files(self, prefix: str) -> list[FileInfo]:
        """列出文件"""
        pass

