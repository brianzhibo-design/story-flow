"""
MinIO 存储后端实现
"""

import io
from datetime import timedelta
from typing import BinaryIO, Optional

import httpx
from minio import Minio
from minio.error import S3Error
import structlog

from app.config import settings
from app.core.storage.base import StorageBackend, UploadResult, FileInfo

logger = structlog.get_logger()


class MinIOBackend(StorageBackend):
    """MinIO 存储后端"""
    
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """确保 Bucket 存在"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info("bucket_created", bucket=self.bucket)
        except S3Error as e:
            logger.error("bucket_error", error=str(e))
    
    async def upload(
        self,
        data: bytes | BinaryIO,
        path: str,
        content_type: str = "application/octet-stream",
        metadata: dict = None
    ) -> UploadResult:
        """上传文件"""
        if isinstance(data, bytes):
            data = io.BytesIO(data)
        
        data.seek(0, 2)
        size = data.tell()
        data.seek(0)
        
        result = self.client.put_object(
            self.bucket, path, data, size,
            content_type=content_type,
            metadata=metadata
        )
        
        logger.info("file_uploaded", path=path, size=size)
        
        return UploadResult(
            path=path,
            url=self._build_url(path),
            size=size,
            content_type=content_type,
            etag=result.etag
        )
    
    async def upload_from_url(self, source_url: str, target_path: str) -> UploadResult:
        """从 URL 下载并上传"""
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.get(source_url)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "application/octet-stream")
            return await self.upload(response.content, target_path, content_type)
    
    async def download(self, path: str) -> bytes:
        """下载文件"""
        response = self.client.get_object(self.bucket, path)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()
    
    async def delete(self, path: str) -> bool:
        """删除文件"""
        try:
            self.client.remove_object(self.bucket, path)
            logger.info("file_deleted", path=path)
            return True
        except S3Error:
            return False
    
    async def exists(self, path: str) -> bool:
        """检查文件是否存在"""
        try:
            self.client.stat_object(self.bucket, path)
            return True
        except S3Error:
            return False
    
    def get_url(self, path: str, expires: int = 3600) -> str:
        """获取访问 URL"""
        if path.startswith("public/"):
            return self._build_url(path)
        return self.client.presigned_get_object(
            self.bucket, path, expires=timedelta(seconds=expires)
        )
    
    async def list_files(self, prefix: str) -> list[FileInfo]:
        """列出文件"""
        files = []
        for obj in self.client.list_objects(self.bucket, prefix=prefix, recursive=True):
            files.append(FileInfo(
                path=obj.object_name,
                size=obj.size or 0,
                content_type=obj.content_type or "application/octet-stream",
                last_modified=obj.last_modified.isoformat() if obj.last_modified else "",
                url=self._build_url(obj.object_name)
            ))
        return files
    
    def _build_url(self, path: str) -> str:
        """构建访问 URL"""
        protocol = "https" if settings.MINIO_SECURE else "http"
        return f"{protocol}://{settings.MINIO_ENDPOINT}/{self.bucket}/{path}"

