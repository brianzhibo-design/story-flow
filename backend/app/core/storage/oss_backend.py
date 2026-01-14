"""
阿里云 OSS 存储后端

官方文档: https://help.aliyun.com/zh/oss/developer-reference/
"""
import oss2
from datetime import datetime
from typing import BinaryIO, Optional, List
from dataclasses import dataclass
import structlog

from app.config import settings
from app.core.storage.base import StorageBackend, UploadResult, FileInfo

logger = structlog.get_logger()


class OSSBackend(StorageBackend):
    """阿里云 OSS 存储后端"""
    
    def __init__(self):
        self.auth = oss2.Auth(
            settings.OSS_ACCESS_KEY_ID,
            settings.OSS_ACCESS_KEY_SECRET
        )
        self.bucket = oss2.Bucket(
            self.auth,
            settings.OSS_ENDPOINT,
            settings.OSS_BUCKET
        )
        self.cdn_domain = settings.OSS_CDN_DOMAIN
        logger.info("oss_backend_initialized", bucket=settings.OSS_BUCKET)
    
    async def upload(
        self,
        data: bytes | BinaryIO,
        path: str,
        content_type: str = "application/octet-stream"
    ) -> UploadResult:
        """上传文件"""
        headers = {"Content-Type": content_type}
        
        if isinstance(data, bytes):
            result = self.bucket.put_object(path, data, headers=headers)
            size = len(data)
        else:
            data.seek(0, 2)
            size = data.tell()
            data.seek(0)
            result = self.bucket.put_object(path, data, headers=headers)
        
        logger.info("oss_file_uploaded", path=path, size=size)
        
        return UploadResult(
            path=path,
            url=self._build_url(path),
            size=size,
            content_type=content_type,
            etag=result.etag
        )
    
    async def upload_from_url(self, source_url: str, target_path: str) -> UploadResult:
        """从 URL 下载并上传到 OSS"""
        import httpx
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.get(source_url)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "application/octet-stream")
            return await self.upload(response.content, target_path, content_type)
    
    async def download(self, path: str) -> bytes:
        """下载文件"""
        result = self.bucket.get_object(path)
        return result.read()
    
    async def delete(self, path: str) -> bool:
        """删除文件"""
        try:
            self.bucket.delete_object(path)
            logger.info("oss_file_deleted", path=path)
            return True
        except Exception as e:
            logger.error("oss_delete_failed", path=path, error=str(e))
            return False
    
    async def exists(self, path: str) -> bool:
        """检查文件是否存在"""
        return self.bucket.object_exists(path)
    
    def get_url(self, path: str, expires: int = 3600) -> str:
        """获取访问 URL"""
        if self._is_public(path):
            return self._build_url(path)
        # 私有文件使用签名 URL
        return self.bucket.sign_url('GET', path, expires)
    
    def get_upload_url(self, path: str, expires: int = 3600) -> str:
        """获取预签名上传 URL (客户端直传)"""
        return self.bucket.sign_url('PUT', path, expires)
    
    async def list_files(self, prefix: str) -> List[FileInfo]:
        """列出文件"""
        files = []
        for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
            files.append(FileInfo(
                path=obj.key,
                size=obj.size,
                content_type="",
                last_modified=obj.last_modified,
                url=self._build_url(obj.key)
            ))
        return files
    
    def _build_url(self, path: str) -> str:
        """构建访问 URL"""
        if self.cdn_domain:
            return f"https://{self.cdn_domain}/{path}"
        return f"https://{settings.OSS_BUCKET}.{settings.OSS_ENDPOINT}/{path}"
    
    def _is_public(self, path: str) -> bool:
        """判断是否为公开路径"""
        return path.startswith("public/") or path.startswith("assets/")
    
    def _ensure_bucket(self):
        """确保 bucket 存在 (OSS 需要提前创建，此处仅检查)"""
        try:
            self.bucket.get_bucket_info()
            logger.info("oss_bucket_exists", bucket=settings.OSS_BUCKET)
        except oss2.exceptions.NoSuchBucket:
            logger.error("oss_bucket_not_found", bucket=settings.OSS_BUCKET)
            raise

