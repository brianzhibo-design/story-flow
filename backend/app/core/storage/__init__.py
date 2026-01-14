"""存储模块"""

from app.config import settings
from app.core.storage.base import StorageBackend, UploadResult, FileInfo

_storage_instance: StorageBackend | None = None


def get_storage() -> StorageBackend:
    """获取存储后端实例"""
    global _storage_instance
    
    if _storage_instance is not None:
        return _storage_instance
    
    if settings.STORAGE_TYPE == "minio":
        from app.core.storage.minio_backend import MinIOBackend
        _storage_instance = MinIOBackend()
    elif settings.STORAGE_TYPE == "oss":
        from app.core.storage.oss_backend import OSSBackend
        _storage_instance = OSSBackend()
    else:
        # 默认使用 MinIO
        from app.core.storage.minio_backend import MinIOBackend
        _storage_instance = MinIOBackend()
    
    return _storage_instance


class _LazyStorageClient:
    """延迟加载的存储客户端"""
    
    def __getattr__(self, name):
        return getattr(get_storage(), name)
    
    def ensure_bucket(self):
        """确保 bucket 存在"""
        try:
            storage = get_storage()
            if hasattr(storage, '_ensure_bucket'):
                storage._ensure_bucket()
        except Exception:
            pass  # 在开发环境中忽略存储连接错误


storage_client = _LazyStorageClient()

__all__ = ["StorageBackend", "UploadResult", "FileInfo", "get_storage", "storage_client"]

