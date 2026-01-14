# backend/app/core/storage.py
"""
存储服务

支持 MinIO 和阿里云 OSS
"""

import io
from typing import BinaryIO, Optional
from datetime import timedelta

import httpx
import structlog
from minio import Minio
from minio.error import S3Error

from app.config import settings
from app.core.exceptions import StorageError, FileNotFoundError

logger = structlog.get_logger()


class StorageClient:
    """对象存储客户端封装"""
    
    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket = settings.MINIO_BUCKET
    
    def ensure_bucket(self) -> None:
        """确保 bucket 存在"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info("bucket_created", bucket=self.bucket)
        except S3Error as e:
            logger.error("bucket_error", error=str(e))
            raise StorageError(f"Failed to create bucket: {e}")
    
    def upload_file(
        self,
        file_path: str,
        data: BinaryIO | bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        上传文件。
        
        Args:
            file_path: 存储路径 (如 "projects/xxx/image.png")
            data: 文件数据
            content_type: 内容类型
            
        Returns:
            文件路径
        """
        try:
            if isinstance(data, bytes):
                data = io.BytesIO(data)
                length = len(data.getvalue())
            else:
                data.seek(0, 2)
                length = data.tell()
                data.seek(0)
            
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=file_path,
                data=data,
                length=length,
                content_type=content_type,
            )
            
            url = self._get_url(file_path)
            logger.info("file_uploaded", path=file_path, size=length)
            return url
            
        except S3Error as e:
            raise StorageError(f"Failed to upload file: {e}")
    
    async def upload_from_url(
        self,
        source_url: str,
        target_path: str
    ) -> str:
        """
        从 URL 下载并上传
        
        Args:
            source_url: 源文件 URL
            target_path: 目标存储路径
            
        Returns:
            文件访问 URL
        """
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.get(source_url)
                response.raise_for_status()
                
                content_type = response.headers.get("content-type", "application/octet-stream")
                file_data = response.content
                
                return self.upload_file(target_path, file_data, content_type)
                
        except Exception as e:
            logger.error("upload_from_url_error", source=source_url, error=str(e))
            raise StorageError(f"Failed to upload from URL: {e}")
    
    def download_file(self, file_path: str) -> bytes:
        """
        下载文件。
        
        Args:
            file_path: 存储路径
            
        Returns:
            文件数据
        """
        try:
            response = self.client.get_object(self.bucket, file_path)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise FileNotFoundError(f"File not found: {file_path}")
            raise StorageError(f"Failed to download file: {e}")
    
    def delete_file(self, file_path: str) -> None:
        """
        删除文件。
        
        Args:
            file_path: 存储路径
        """
        try:
            self.client.remove_object(self.bucket, file_path)
            logger.info("file_deleted", path=file_path)
        except S3Error as e:
            raise StorageError(f"Failed to delete file: {e}")
    
    def get_presigned_url(
        self,
        file_path: str,
        expires: timedelta = timedelta(hours=1),
    ) -> str:
        """
        获取预签名URL。
        
        Args:
            file_path: 存储路径
            expires: 过期时间
            
        Returns:
            预签名URL
        """
        try:
            return self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=file_path,
                expires=expires,
            )
        except S3Error as e:
            raise StorageError(f"Failed to get presigned URL: {e}")
    
    def _get_url(self, path: str) -> str:
        """获取文件访问 URL"""
        protocol = "https" if settings.MINIO_SECURE else "http"
        return f"{protocol}://{settings.MINIO_ENDPOINT}/{self.bucket}/{path}"
    
    def get_public_url(self, file_path: str) -> str:
        """
        获取公开访问URL。
        
        Args:
            file_path: 存储路径
            
        Returns:
            公开URL
        """
        return self._get_url(file_path)
    
    def file_exists(self, file_path: str) -> bool:
        """
        检查文件是否存在。
        
        Args:
            file_path: 存储路径
            
        Returns:
            是否存在
        """
        try:
            self.client.stat_object(self.bucket, file_path)
            return True
        except S3Error:
            return False


# 全局实例
storage_client = StorageClient()


def get_storage() -> StorageClient:
    """获取存储客户端依赖"""
    return storage_client
