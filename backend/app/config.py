# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional, Union
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # === 应用配置 ===
    APP_NAME: str = "StoryFlow"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # === 安全配置 ===
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-12345678",
        description="JWT密钥"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # === 数据库配置 ===
    # 默认使用 SQLite 方便本地开发，生产环境使用 PostgreSQL
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./storyflow_dev.db",
        description="数据库连接URL"
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # === Redis配置 ===
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # === RabbitMQ配置 ===
    RABBITMQ_URL: str = Field(default="amqp://guest:guest@localhost:5672/")
    
    # === 存储配置 ===
    STORAGE_TYPE: str = "minio"  # minio | oss | local
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "storyflow"
    MINIO_SECURE: bool = False
    
    # === AI Mock 模式 (开发测试) ===
    AI_MOCK_MODE: bool = True  # 开发时设为 True，生产时设为 False
    
    # === 通义大模型 (DashScope) ===
    DASHSCOPE_API_KEY: Optional[str] = None
    QWEN_MODEL: str = "qwen-plus"  # qwen-max / qwen-plus / qwen-turbo
    WANX_MODEL: str = "wanx-v1"
    
    # === DeepSeek (备选 LLM) ===
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    
    # === 智谱 GLM (备选 LLM) ===
    ZHIPU_API_KEY: Optional[str] = None
    
    # === 即梦 (备选图片生成) ===
    JIMENG_API_KEY: Optional[str] = None
    JIMENG_BASE_URL: str = "https://api.jimeng.jianying.com"
    
    # === 可灵 (视频生成) ===
    KLING_API_KEY: Optional[str] = None
    KLING_ACCESS_KEY: Optional[str] = None
    KLING_SECRET_KEY: Optional[str] = None
    KLING_BASE_URL: str = "https://api.klingai.com"
    
    # === ComfyUI配置 ===
    COMFYUI_URL: Optional[str] = None  # e.g., "http://localhost:8188"
    
    # === 阿里云 OSS 配置 ===
    OSS_ACCESS_KEY_ID: Optional[str] = None
    OSS_ACCESS_KEY_SECRET: Optional[str] = None
    OSS_BUCKET: Optional[str] = None
    OSS_ENDPOINT: Optional[str] = None
    OSS_CDN_DOMAIN: Optional[str] = None
    
    # === 火山引擎 TTS 配置 ===
    VOLCENGINE_TTS_APP_ID: Optional[str] = None
    VOLCENGINE_TTS_TOKEN: Optional[str] = None
    
    # === 模型选择策略 ===
    DEFAULT_CHECKPOINT: str = "sd_xl_base_1.0.safetensors"
    REALISTIC_CHECKPOINT: str = "realisticVisionV51_v51VAE.safetensors"
    ANIME_CHECKPOINT: str = "animePastelDream_v2.safetensors"
    
    # === ControlNet 模型 ===
    CONTROLNET_OPENPOSE: str = "control_v11p_sd15_openpose"
    CONTROLNET_DEPTH: str = "control_v11f1p_sd15_depth"
    CONTROLNET_CANNY: str = "control_v11p_sd15_canny"
    CONTROLNET_INPAINT: str = "control_v11p_sd15_inpaint"
    
    # === 画质增强配置 ===
    ENABLE_FACE_FIX: bool = True
    ENABLE_HAND_FIX: bool = True
    AUTO_UPSCALE_THRESHOLD: int = 720  # 低于此分辨率自动超分
    DEFAULT_UPSCALE_METHOD: str = "RealESRGAN_x4plus"
    
    # === 安全运动强度 ===
    MAX_MOTION_INTENSITY_CLOSEUP: float = 0.3
    MAX_MOTION_INTENSITY_MEDIUM: float = 0.5
    MAX_MOTION_INTENSITY_WIDE: float = 0.8
    
    # === CORS配置 ===
    # 支持字符串（逗号分隔）或列表格式
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, list]) -> list[str]:
        """解析 CORS origins - 支持逗号分隔的字符串或列表"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # === 支付宝配置 ===
    ALIPAY_APP_ID: Optional[str] = None
    ALIPAY_PRIVATE_KEY: Optional[str] = None
    ALIPAY_PUBLIC_KEY: Optional[str] = None
    ALIPAY_NOTIFY_URL: str = "https://your-domain.com/api/v1/payment/notify/alipay"
    ALIPAY_RETURN_URL: str = "https://your-domain.com/payment/success"
    ALIPAY_GATEWAY: str = "https://openapi.alipay.com/gateway.do"
    
    # === 微信支付配置 ===
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_MCH_ID: Optional[str] = None
    WECHAT_API_V3_KEY: Optional[str] = None
    WECHAT_PRIVATE_KEY: Optional[str] = None
    WECHAT_CERT_SERIAL_NO: Optional[str] = None
    WECHAT_NOTIFY_URL: str = "https://your-domain.com/api/v1/payment/notify/wechat"


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
