"""
ComfyUI 供应商

支持 IP-Adapter 实现角色一致性
"""

import asyncio
import httpx
import structlog

from app.config import settings
from app.ai_gateway.providers.base import BaseImageProvider

logger = structlog.get_logger()


class ComfyUIProvider(BaseImageProvider):
    """ComfyUI 图片生成供应商"""
    
    def __init__(self):
        self.base_url = settings.COMFYUI_URL or "http://localhost:8188"
    
    async def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 576,
        **kwargs
    ) -> dict:
        """普通图片生成"""
        workflow = self._build_basic_workflow(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            seed=kwargs.get("seed", -1)
        )
        return await self._execute_workflow(workflow)
    
    async def generate_with_reference(
        self,
        prompt: str,
        reference_image_url: str,
        ip_adapter_scale: float = 0.6,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 576,
        seed: int = -1,
        **kwargs
    ) -> dict:
        """使用参考图生成（IP-Adapter）"""
        
        async with httpx.AsyncClient(timeout=300) as client:
            # 1. 上传参考图到 ComfyUI
            ref_name = await self._upload_reference(client, reference_image_url)
            
            # 2. 构建 IP-Adapter 工作流
            workflow = self._build_ip_adapter_workflow(
                prompt=prompt,
                negative_prompt=negative_prompt,
                reference_image=ref_name,
                ip_adapter_scale=ip_adapter_scale,
                width=width,
                height=height,
                seed=seed
            )
            
            # 3. 执行
            return await self._execute_workflow(workflow, client)
    
    async def generate_with_multi_reference(
        self,
        prompt: str,
        references: list[dict],
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 576,
        seed: int = -1
    ) -> dict:
        """
        多参考图生成
        
        references: [{"image_url": "...", "weight": 0.6}, ...]
        """
        async with httpx.AsyncClient(timeout=300) as client:
            # 上传所有参考图
            ref_names = []
            for ref in references:
                name = await self._upload_reference(client, ref["image_url"])
                ref_names.append({"name": name, "weight": ref.get("weight", 0.5)})
            
            # 构建多参考工作流
            workflow = self._build_multi_ip_adapter_workflow(
                prompt=prompt,
                negative_prompt=negative_prompt,
                references=ref_names,
                width=width,
                height=height,
                seed=seed
            )
            
            return await self._execute_workflow(workflow, client)
    
    async def _upload_reference(self, client: httpx.AsyncClient, image_url: str) -> str:
        """上传参考图到 ComfyUI"""
        # 下载图片
        img_response = await client.get(image_url)
        img_data = img_response.content
        
        # 上传
        files = {"image": ("reference.png", img_data, "image/png")}
        response = await client.post(f"{self.base_url}/upload/image", files=files)
        return response.json()["name"]
    
    async def _execute_workflow(self, workflow: dict, client: httpx.AsyncClient = None) -> dict:
        """执行工作流"""
        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=300)
            should_close = True
        
        try:
            # 提交
            response = await client.post(
                f"{self.base_url}/prompt",
                json={"prompt": workflow}
            )
            response.raise_for_status()
            prompt_id = response.json()["prompt_id"]
            
            # 等待完成
            return await self._wait_completion(client, prompt_id)
        finally:
            if should_close:
                await client.aclose()
    
    async def _wait_completion(self, client: httpx.AsyncClient, prompt_id: str, timeout: int = 300) -> dict:
        """等待工作流完成"""
        start = asyncio.get_event_loop().time()
        
        while True:
            if asyncio.get_event_loop().time() - start > timeout:
                raise TimeoutError("ComfyUI timeout")
            
            response = await client.get(f"{self.base_url}/history/{prompt_id}")
            history = response.json()
            
            if prompt_id in history:
                outputs = history[prompt_id]["outputs"]
                for node_id, output in outputs.items():
                    if "images" in output:
                        img = output["images"][0]
                        return {
                            "image_url": f"{self.base_url}/view?filename={img['filename']}",
                            "filename": img["filename"],
                            "seed": history[prompt_id].get("seed")
                        }
            
            await asyncio.sleep(2)
    
    def _build_basic_workflow(self, prompt: str, negative_prompt: str, width: int, height: int, seed: int) -> dict:
        """基础工作流"""
        return {
            "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
            "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
            "3": {"class_type": "CLIPTextEncode", "inputs": {"text": negative_prompt or "bad quality", "clip": ["1", 1]}},
            "4": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
            "5": {"class_type": "KSampler", "inputs": {
                "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
                "latent_image": ["4", 0], "seed": seed, "steps": 30, "cfg": 7,
                "sampler_name": "euler_ancestral", "scheduler": "normal", "denoise": 1
            }},
            "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
            "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "storyflow"}}
        }
    
    def _build_ip_adapter_workflow(
        self,
        prompt: str,
        negative_prompt: str,
        reference_image: str,
        ip_adapter_scale: float,
        width: int,
        height: int,
        seed: int
    ) -> dict:
        """IP-Adapter 工作流"""
        return {
            "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
            "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
            "3": {"class_type": "CLIPTextEncode", "inputs": {"text": negative_prompt or "bad quality", "clip": ["1", 1]}},
            "4": {"class_type": "IPAdapterModelLoader", "inputs": {"ipadapter_file": "ip-adapter-plus_sdxl_vit-h.safetensors"}},
            "5": {"class_type": "CLIPVisionLoader", "inputs": {"clip_name": "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"}},
            "6": {"class_type": "LoadImage", "inputs": {"image": reference_image}},
            "7": {"class_type": "IPAdapterApply", "inputs": {
                "model": ["1", 0], "ipadapter": ["4", 0], "clip_vision": ["5", 0],
                "image": ["6", 0], "weight": ip_adapter_scale, "noise": 0.2,
                "weight_type": "linear", "start_at": 0, "end_at": 1
            }},
            "8": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
            "9": {"class_type": "KSampler", "inputs": {
                "model": ["7", 0], "positive": ["2", 0], "negative": ["3", 0],
                "latent_image": ["8", 0], "seed": seed, "steps": 30, "cfg": 7,
                "sampler_name": "euler_ancestral", "scheduler": "normal", "denoise": 1
            }},
            "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["1", 2]}},
            "11": {"class_type": "SaveImage", "inputs": {"images": ["10", 0], "filename_prefix": "storyflow"}}
        }
    
    def _build_multi_ip_adapter_workflow(self, prompt: str, negative_prompt: str, references: list[dict], width: int, height: int, seed: int) -> dict:
        """多参考图工作流（简化版，实际需要更复杂的节点链接）"""
        # 使用第一个参考图
        return self._build_ip_adapter_workflow(
            prompt, negative_prompt,
            references[0]["name"],
            references[0]["weight"],
            width, height, seed
        )
    
    async def check_health(self) -> bool:
        """健康检查"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/system_stats")
                return response.status_code == 200
        except Exception:
            return False

