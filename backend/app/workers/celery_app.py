"""
Celery 应用配置

任务队列配置和初始化
"""

from celery import Celery
from kombu import Exchange, Queue

from app.config import settings

# 创建 Celery 应用
celery_app = Celery(
    "storyflow",
    broker=settings.RABBITMQ_URL,
    backend=f"{settings.REDIS_URL}/1",  # 使用 Redis DB 1 存储结果
)

# ==================== 基础配置 ====================
celery_app.conf.update(
    # 时区
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # 序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 结果配置
    result_expires=86400,  # 结果保存24小时
    result_extended=True,  # 保存额外信息
    
    # 任务配置
    task_track_started=True,  # 追踪任务开始状态
    task_time_limit=600,  # 任务超时10分钟
    task_soft_time_limit=540,  # 软超时9分钟
    
    # Worker 配置
    worker_prefetch_multiplier=1,  # 每次只取一个任务
    worker_concurrency=4,  # 并发数
    
    # 重试配置
    task_acks_late=True,  # 任务完成后才确认
    task_reject_on_worker_lost=True,  # Worker 丢失时拒绝任务
)

# ==================== 队列定义 ====================
default_exchange = Exchange("default", type="direct")
storyboard_exchange = Exchange("storyboard", type="direct")
image_exchange = Exchange("image", type="direct")
video_exchange = Exchange("video", type="direct")

compose_exchange = Exchange("compose", type="direct")

celery_app.conf.task_queues = (
    # 默认队列
    Queue("default", default_exchange, routing_key="default"),
    
    # 分镜生成队列
    Queue("storyboard", storyboard_exchange, routing_key="storyboard"),
    
    # 图片生成队列
    Queue("image", image_exchange, routing_key="image"),
    
    # 视频生成队列
    Queue("video", video_exchange, routing_key="video"),
    
    # 视频合成队列
    Queue("compose", compose_exchange, routing_key="compose"),
)

# 默认队列
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_default_exchange = "default"
celery_app.conf.task_default_routing_key = "default"

# ==================== 任务路由 ====================
celery_app.conf.task_routes = {
    # 分镜任务路由到 storyboard 队列
    "app.workers.storyboard.*": {
        "queue": "storyboard",
        "routing_key": "storyboard",
    },
    # 图片任务路由到 image 队列
    "app.workers.image.*": {
        "queue": "image",
        "routing_key": "image",
    },
    # 视频任务路由到 video 队列
    "app.workers.video.*": {
        "queue": "video",
        "routing_key": "video",
    },
    # 视频合成任务路由到 compose 队列
    "app.workers.compose.*": {
        "queue": "compose",
        "routing_key": "compose",
    },
}

# ==================== 任务优先级 ====================
celery_app.conf.task_queue_max_priority = 10
celery_app.conf.task_default_priority = 5

# ==================== 任务限流 ====================
celery_app.conf.task_annotations = {
    "app.workers.image.generate_image": {
        "rate_limit": "10/m"  # 每分钟最多10个
    },
    "app.workers.video.generate_video": {
        "rate_limit": "5/m"
    },
}

# ==================== 自动发现任务 ====================
celery_app.autodiscover_tasks([
    "app.workers.storyboard",
    "app.workers.image",
    "app.workers.video",
    "app.workers.compose",
])


# ==================== 信号处理 ====================
from celery.signals import task_prerun, task_postrun, task_failure

@task_prerun.connect
def task_prerun_handler(task_id, task, args, kwargs, **kw):
    """任务开始前"""
    import structlog
    logger = structlog.get_logger()
    logger.info("task_started", task_id=task_id, task_name=task.name)


@task_postrun.connect
def task_postrun_handler(task_id, task, args, kwargs, retval, state, **kw):
    """任务完成后"""
    import structlog
    logger = structlog.get_logger()
    logger.info("task_completed", task_id=task_id, task_name=task.name, state=state)


@task_failure.connect
def task_failure_handler(task_id, exception, args, kwargs, traceback, einfo, **kw):
    """任务失败"""
    import structlog
    logger = structlog.get_logger()
    logger.error("task_failed", task_id=task_id, error=str(exception))
