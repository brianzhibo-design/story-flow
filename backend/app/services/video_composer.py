"""
视频合成服务

使用 FFmpeg 合成最终视频
"""

import asyncio
import tempfile
from pathlib import Path

import httpx
import structlog

from app.services.file_service import get_file_service

logger = structlog.get_logger()


class VideoComposer:
    """视频合成器"""
    
    def __init__(self):
        self.file_service = get_file_service()
    
    async def compose_project(
        self,
        project_id: str,
        scenes: list[dict],
        config: dict = None
    ) -> dict:
        """
        合成项目视频
        
        scenes: [
            {
                "video_url": "...",
                "audio_url": "...",  # 可选
                "duration": 5.0,
                "text": "字幕文本"  # 可选
            },
            ...
        ]
        
        config: {
            "resolution": "1920x1080",
            "fps": 24,
            "transition": "fade",  # none/fade/dissolve
            "transition_duration": 0.5,
            "bgm_url": "...",  # 背景音乐
            "bgm_volume": 0.3,
            "subtitle": true,
            "subtitle_style": "..."
        }
        """
        config = config or {}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # 1. 下载所有素材
            logger.info("downloading_assets", project_id=project_id)
            scene_files = await self._download_assets(scenes, tmpdir)
            
            # 2. 处理每个分镜
            logger.info("processing_scenes", count=len(scenes))
            processed = await self._process_scenes(scene_files, tmpdir, config)
            
            # 3. 生成合并列表
            concat_file = tmpdir / "concat.txt"
            with open(concat_file, "w") as f:
                for p in processed:
                    f.write(f"file '{p}'\n")
            
            # 4. 合并视频
            output_file = tmpdir / "output.mp4"
            await self._concat_videos(concat_file, output_file, config)
            
            # 5. 添加背景音乐
            if config.get("bgm_url"):
                final_file = tmpdir / "final.mp4"
                await self._add_bgm(output_file, config["bgm_url"], final_file, config)
                output_file = final_file
            
            # 6. 上传最终视频
            with open(output_file, "rb") as f:
                result = await self.file_service.save_final_video(
                    project_id=project_id,
                    data=f.read()
                )
            
            logger.info("composition_complete", project_id=project_id, url=result.url)
            
            return {
                "video_url": result.url,
                "size": result.size
            }
    
    async def _download_assets(self, scenes: list[dict], tmpdir: Path) -> list[dict]:
        """下载素材"""
        result = []
        
        async with httpx.AsyncClient(timeout=120) as client:
            for i, scene in enumerate(scenes):
                files = {"index": i}
                
                # 下载视频
                if scene.get("video_url"):
                    video_path = tmpdir / f"scene_{i}_video.mp4"
                    resp = await client.get(scene["video_url"])
                    with open(video_path, "wb") as f:
                        f.write(resp.content)
                    files["video"] = str(video_path)
                
                # 下载音频
                if scene.get("audio_url"):
                    audio_path = tmpdir / f"scene_{i}_audio.mp3"
                    resp = await client.get(scene["audio_url"])
                    with open(audio_path, "wb") as f:
                        f.write(resp.content)
                    files["audio"] = str(audio_path)
                
                files["duration"] = scene.get("duration", 5)
                files["text"] = scene.get("text", "")
                
                result.append(files)
        
        return result
    
    async def _process_scenes(
        self,
        scene_files: list[dict],
        tmpdir: Path,
        config: dict
    ) -> list[str]:
        """处理分镜：合并音视频、添加字幕"""
        processed = []
        
        for files in scene_files:
            i = files["index"]
            output = tmpdir / f"processed_{i}.mp4"
            
            video = files.get("video")
            audio = files.get("audio")
            text = files.get("text")
            
            if not video:
                continue
            
            # 构建 FFmpeg 命令
            cmd = ["ffmpeg", "-y", "-i", video]
            
            # 添加音频
            if audio:
                cmd.extend(["-i", audio])
                # 混合视频原声和配音
                cmd.extend(["-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first[a]"])
                cmd.extend(["-map", "0:v", "-map", "[a]"])
            
            # 添加字幕
            if text and config.get("subtitle"):
                # 使用 drawtext 滤镜
                subtitle_style = config.get("subtitle_style", "fontsize=24:fontcolor=white:borderw=2:bordercolor=black")
                escaped_text = text.replace("'", "\\'").replace(":", "\\:")
                cmd.extend(["-vf", f"drawtext=text='{escaped_text}':{subtitle_style}:x=(w-text_w)/2:y=h-50"])
            
            cmd.extend(["-c:v", "libx264", "-c:a", "aac", str(output)])
            
            # 执行
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            
            if output.exists():
                processed.append(str(output))
        
        return processed
    
    async def _concat_videos(self, concat_file: Path, output: Path, config: dict):
        """合并视频"""
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c:v", "libx264", "-c:a", "aac", str(output)
        ]
        
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
    
    async def _add_bgm(self, video: Path, bgm_url: str, output: Path, config: dict):
        """添加背景音乐"""
        # 下载 BGM
        async with httpx.AsyncClient() as client:
            resp = await client.get(bgm_url)
            bgm_file = video.parent / "bgm.mp3"
            with open(bgm_file, "wb") as f:
                f.write(resp.content)
        
        volume = config.get("bgm_volume", 0.3)
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video),
            "-i", str(bgm_file),
            "-filter_complex", f"[1:a]volume={volume}[bgm];[0:a][bgm]amix=inputs=2:duration=first[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac",
            str(output)
        ]
        
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()

