"""
AI Gateway 路由器

统一管理所有 AI 供应商，支持：
- 自动健康检查
- 故障转移
- Mock 模式 (开发测试)
- 负载均衡 (可选)
"""
import json
import structlog
from typing import Optional, List

from app.config import settings
from app.core.redis import redis_client
from app.core.exceptions import AIProviderUnavailableError
from app.ai_gateway.providers.base import BaseLLMProvider, BaseImageProvider, BaseVideoProvider
from app.ai_gateway.providers.tts_base import BaseTTSProvider

logger = structlog.get_logger()


class AIGateway:
    """AI Gateway - 统一的 AI 服务入口"""
    
    def __init__(self):
        self._llm_providers: dict[str, BaseLLMProvider] = {}
        self._image_providers: dict[str, BaseImageProvider] = {}
        self._video_providers: dict[str, BaseVideoProvider] = {}
        self._tts_providers: dict[str, BaseTTSProvider] = {}
        self._initialized = False
        self._mock_mode = getattr(settings, 'AI_MOCK_MODE', False)
    
    async def _init_providers(self):
        """延迟初始化供应商"""
        if self._initialized:
            return
        
        # Mock 模式
        if self._mock_mode:
            logger.info("🔧 AI Gateway 运行在 Mock 模式")
            from app.ai_gateway.providers.mock import (
                MockLLMProvider, MockImageProvider, 
                MockVideoProvider, MockTTSProvider
            )
            self._llm_providers["mock"] = MockLLMProvider()
            self._image_providers["mock"] = MockImageProvider()
            self._video_providers["mock"] = MockVideoProvider()
            self._tts_providers["mock"] = MockTTSProvider()
            self._initialized = True
            return
        
        # ==================== LLM 供应商 ====================
        
        # 通义千问 (优先)
        if getattr(settings, 'DASHSCOPE_API_KEY', None):
            try:
                from app.ai_gateway.providers.qwen import QwenProvider
                self._llm_providers["qwen"] = QwenProvider()
                logger.info("✓ 通义千问 LLM 已启用")
            except Exception as e:
                logger.error("qwen_init_failed", error=str(e))
        
        # DeepSeek (备选)
        if getattr(settings, 'DEEPSEEK_API_KEY', None):
            try:
                from app.ai_gateway.providers.deepseek import DeepSeekProvider
                self._llm_providers["deepseek"] = DeepSeekProvider()
                logger.info("✓ DeepSeek LLM 已启用")
            except Exception as e:
                logger.error("deepseek_init_failed", error=str(e))
        
        # 智谱 GLM (备选)
        if getattr(settings, 'ZHIPU_API_KEY', None):
            try:
                from app.ai_gateway.providers.zhipu import ZhipuProvider
                self._llm_providers["zhipu"] = ZhipuProvider()
                logger.info("✓ 智谱 GLM 已启用")
            except Exception as e:
                logger.error("zhipu_init_failed", error=str(e))
        
        # ==================== 图片生成供应商 ====================
        
        # 通义万相 (优先)
        if getattr(settings, 'DASHSCOPE_API_KEY', None):
            try:
                from app.ai_gateway.providers.wanx import WanxProvider
                self._image_providers["wanx"] = WanxProvider()
                logger.info("✓ 通义万相已启用")
            except Exception as e:
                logger.error("wanx_init_failed", error=str(e))
        
        # 即梦 (备选)
        if getattr(settings, 'JIMENG_API_KEY', None):
            try:
                from app.ai_gateway.providers.jimeng import JimengImageProvider
                self._image_providers["jimeng"] = JimengImageProvider()
                logger.info("✓ 即梦已启用")
            except Exception as e:
                logger.error("jimeng_init_failed", error=str(e))
        
        # ==================== 视频生成供应商 ====================
        
        # 可灵 (优先)
        if getattr(settings, 'KLING_ACCESS_KEY', None) or getattr(settings, 'KLING_API_KEY', None):
            try:
                from app.ai_gateway.providers.kling import KlingProvider
                self._video_providers["kling"] = KlingProvider()
                logger.info("✓ 可灵已启用")
            except Exception as e:
                logger.error("kling_init_failed", error=str(e))
        
        # ==================== TTS 供应商 ====================
        
        # 阿里云 TTS (优先)
        if getattr(settings, 'DASHSCOPE_API_KEY', None):
            try:
                from app.ai_gateway.providers.aliyun_tts import AliyunTTSProvider
                self._tts_providers["aliyun"] = AliyunTTSProvider()
                logger.info("✓ 阿里云 TTS 已启用")
            except Exception as e:
                logger.error("aliyun_tts_init_failed", error=str(e))
        
        # 火山引擎 TTS (备选)
        if getattr(settings, 'VOLCENGINE_TTS_APP_ID', None):
            try:
                from app.ai_gateway.providers.volcengine_tts import VolcengineTTSProvider
                self._tts_providers["volcengine"] = VolcengineTTSProvider()
                logger.info("✓ 火山引擎 TTS 已启用")
            except Exception as e:
                logger.error("volcengine_tts_init_failed", error=str(e))
        
        self._initialized = True
        
        # 打印初始化状态
        logger.info(
            "ai_gateway_initialized",
            llm_providers=list(self._llm_providers.keys()),
            image_providers=list(self._image_providers.keys()),
            video_providers=list(self._video_providers.keys()),
            tts_providers=list(self._tts_providers.keys())
        )
    
    # ==================== LLM 接口 ====================
    
    async def get_llm_provider(self, preferred: str = None) -> BaseLLMProvider:
        """
        获取 LLM 供应商
        
        优先级: 指定 > qwen > deepseek > mock
        """
        await self._init_providers()
        
        if preferred and preferred in self._llm_providers:
            return self._llm_providers[preferred]
        
        # 默认优先级
        for name in ["qwen", "deepseek", "zhipu", "mock"]:
            if name in self._llm_providers:
                provider = self._llm_providers[name]
                if await self._check_health("llm", name, provider):
                    return provider
        
        raise AIProviderUnavailableError("没有可用的 LLM 供应商")
    
    async def chat(
        self,
        messages: List[dict],
        provider: str = None,
        **kwargs
    ) -> str:
        """统一的聊天接口"""
        llm = await self.get_llm_provider(provider)
        return await llm.chat_completion(messages, **kwargs)
    
    async def chat_json(
        self,
        messages: List[dict],
        provider: str = None,
        **kwargs
    ) -> dict:
        """JSON 模式聊天"""
        llm = await self.get_llm_provider(provider)
        if hasattr(llm, 'chat_json'):
            return await llm.chat_json(messages, **kwargs)
        
        # 降级处理
        response = await llm.chat_completion(
            messages, 
            response_format={"type": "json_object"},
            **kwargs
        )
        return json.loads(response)
    
    # ==================== 图片生成接口 ====================
    
    async def get_image_provider(self, preferred: str = None) -> BaseImageProvider:
        """
        获取图片生成供应商
        
        优先级: 指定 > wanx > jimeng > mock
        """
        await self._init_providers()
        
        if preferred and preferred in self._image_providers:
            return self._image_providers[preferred]
        
        for name in ["wanx", "jimeng", "mock"]:
            if name in self._image_providers:
                provider = self._image_providers[name]
                if await self._check_health("image", name, provider):
                    return provider
        
        raise AIProviderUnavailableError("没有可用的图片生成供应商")
    
    async def generate_image(
        self,
        prompt: str,
        provider: str = None,
        **kwargs
    ) -> dict:
        """统一的图片生成接口"""
        img_provider = await self.get_image_provider(provider)
        return await img_provider.generate(prompt, **kwargs)
    
    # ==================== 视频生成接口 ====================
    
    async def get_video_provider(self, preferred: str = None) -> BaseVideoProvider:
        """获取视频生成供应商"""
        await self._init_providers()
        
        if preferred and preferred in self._video_providers:
            return self._video_providers[preferred]
        
        for name in ["kling", "jimeng", "mock"]:
            if name in self._video_providers:
                provider = self._video_providers[name]
                if await self._check_health("video", name, provider):
                    return provider
        
        raise AIProviderUnavailableError("没有可用的视频生成供应商")
    
    async def generate_video(
        self,
        image_url: str,
        prompt: str = "",
        provider: str = None,
        **kwargs
    ) -> dict:
        """统一的视频生成接口 (图生视频)"""
        video_provider = await self.get_video_provider(provider)
        return await video_provider.generate(image_url, prompt, **kwargs)
    
    # ==================== TTS 接口 ====================
    
    async def get_tts_provider(self, preferred: str = None) -> BaseTTSProvider:
        """获取 TTS 供应商"""
        await self._init_providers()
        
        if preferred and preferred in self._tts_providers:
            return self._tts_providers[preferred]
        
        for name in ["aliyun", "volcengine", "mock"]:
            if name in self._tts_providers:
                return self._tts_providers[name]
        
        raise AIProviderUnavailableError("没有可用的 TTS 供应商")
    
    async def synthesize_speech(
        self,
        text: str,
        voice: str = "zhixiaobai",
        provider: str = None,
        **kwargs
    ) -> dict:
        """统一的语音合成接口"""
        tts = await self.get_tts_provider(provider)
        return await tts.synthesize(text, voice=voice, **kwargs)
    
    async def get_voices(self, provider: str = None) -> List[dict]:
        """获取可用音色列表"""
        tts = await self.get_tts_provider(provider)
        return await tts.get_voices()
    
    # ==================== 健康检查 ====================
    
    async def _check_health(self, type: str, name: str, provider) -> bool:
        """检查供应商健康状态（带缓存）"""
        cache_key = f"provider_health:{type}:{name}"
        
        # 先查缓存
        try:
            cached = await redis_client.get(cache_key)
            if cached is not None:
                return cached == "1"
        except Exception:
            pass  # Redis 不可用时跳过缓存
        
        # 检查健康状态
        try:
            is_healthy = await provider.check_health()
            try:
                await redis_client.set(cache_key, "1" if is_healthy else "0", expire=60)
            except Exception:
                pass
            return is_healthy
        except Exception as e:
            logger.warning("provider_health_check_failed", provider=name, error=str(e))
            try:
                await redis_client.set(cache_key, "0", expire=60)
            except Exception:
                pass
            return False
    
    async def health_check(self) -> dict:
        """检查所有供应商健康状态"""
        await self._init_providers()
        
        status = {
            "mock_mode": self._mock_mode,
            "llm": {},
            "image": {},
            "video": {},
            "tts": {}
        }
        
        for name, provider in self._llm_providers.items():
            status["llm"][name] = await provider.check_health()
        
        for name, provider in self._image_providers.items():
            status["image"][name] = await provider.check_health()
        
        for name, provider in self._video_providers.items():
            status["video"][name] = await provider.check_health()
        
        for name, provider in self._tts_providers.items():
            status["tts"][name] = await provider.check_health()
        
        return status


# 全局实例
_gateway: AIGateway = None


def get_ai_gateway() -> AIGateway:
    """获取 AI Gateway 实例"""
    global _gateway
    if _gateway is None:
        _gateway = AIGateway()
    return _gateway


# 兼容旧代码
AIProviderRouter = AIGateway
