"""
文件服务

封装业务层的文件操作
"""

from typing import BinaryIO
from app.core.storage import get_storage, UploadResult


class FileService:
    """项目文件服务"""
    
    def __init__(self):
        self.storage = get_storage()
    
    # ==================== 元素参考图 ====================
    
    async def upload_element_reference(
        self,
        project_id: str,
        element_type: str,
        element_id: str,
        data: bytes | BinaryIO,
        index: int = 1
    ) -> UploadResult:
        """上传元素参考图"""
        path = f"projects/{project_id}/elements/{element_type}s/{element_id}/reference_{index}.png"
        return await self.storage.upload(data, path, "image/png")
    
    async def save_element_generated(
        self,
        project_id: str,
        element_type: str,
        element_id: str,
        appearance_id: str,
        source_url: str
    ) -> UploadResult:
        """保存元素生成的图片"""
        path = f"projects/{project_id}/elements/{element_type}s/{element_id}/generated/{appearance_id}.png"
        return await self.storage.upload_from_url(source_url, path)
    
    # ==================== 分镜文件 ====================
    
    async def save_scene_image(
        self,
        project_id: str,
        scene_id: str,
        source_url: str,
        version: int = 1
    ) -> UploadResult:
        """保存分镜图片"""
        suffix = "" if version == 1 else f"_v{version}"
        path = f"projects/{project_id}/scenes/{scene_id}/image{suffix}.png"
        return await self.storage.upload_from_url(source_url, path)
    
    async def save_scene_video(
        self,
        project_id: str,
        scene_id: str,
        source_url: str
    ) -> UploadResult:
        """保存分镜视频"""
        path = f"projects/{project_id}/scenes/{scene_id}/video.mp4"
        return await self.storage.upload_from_url(source_url, path)
    
    async def save_scene_audio(
        self,
        project_id: str,
        scene_id: str,
        data: bytes | BinaryIO
    ) -> UploadResult:
        """保存分镜配音"""
        path = f"projects/{project_id}/scenes/{scene_id}/audio.mp3"
        return await self.storage.upload(data, path, "audio/mpeg")
    
    # ==================== 输出文件 ====================
    
    async def save_final_video(
        self,
        project_id: str,
        data: bytes | BinaryIO
    ) -> UploadResult:
        """保存最终视频"""
        path = f"projects/{project_id}/outputs/final.mp4"
        return await self.storage.upload(data, path, "video/mp4")
    
    # ==================== 获取 URL ====================
    
    def get_element_reference_url(
        self,
        project_id: str,
        element_type: str,
        element_id: str,
        index: int = 1
    ) -> str:
        """获取元素参考图 URL"""
        path = f"projects/{project_id}/elements/{element_type}s/{element_id}/reference_{index}.png"
        return self.storage.get_url(path)
    
    def get_scene_image_url(self, project_id: str, scene_id: str) -> str:
        """获取分镜图片 URL"""
        path = f"projects/{project_id}/scenes/{scene_id}/image.png"
        return self.storage.get_url(path)
    
    def get_scene_video_url(self, project_id: str, scene_id: str) -> str:
        """获取分镜视频 URL"""
        path = f"projects/{project_id}/scenes/{scene_id}/video.mp4"
        return self.storage.get_url(path)
    
    # ==================== 清理 ====================
    
    async def delete_project_files(self, project_id: str) -> int:
        """删除项目所有文件"""
        prefix = f"projects/{project_id}/"
        files = await self.storage.list_files(prefix)
        
        deleted = 0
        for file in files:
            if await self.storage.delete(file.path):
                deleted += 1
        return deleted


# 全局实例
_file_service: FileService | None = None


def get_file_service() -> FileService:
    """获取文件服务实例"""
    global _file_service
    if _file_service is None:
        _file_service = FileService()
    return _file_service

