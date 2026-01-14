"""
AI 供应商智能路由

支持:
- 成本优化路由
- 质量优先路由
- 负载均衡
- 故障转移
- 实时健康监控
"""
import time
import asyncio
import structlog
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum

from app.config import settings

logger = structlog.get_logger()


class RouteStrategy(Enum):
    """路由策略"""
    COST = "cost"           # 成本最低
    QUALITY = "quality"     # 质量最高
    BALANCED = "balanced"   # 综合平衡
    FASTEST = "fastest"     # 最快响应
    ROUND_ROBIN = "round_robin"  # 轮询


@dataclass
class ProviderConfig:
    """供应商配置"""
    name: str
    provider_id: str
    priority: int = 5          # 1-10, 越高越优先
    cost_per_call: float = 0.01
    avg_latency: float = 1.0   # 秒
    success_rate: float = 0.99 # 0-1
    is_available: bool = True
    last_check: float = 0
    failure_count: int = 0
    total_calls: int = 0
    total_latency: float = 0


@dataclass
class ProviderMetrics:
    """供应商实时指标"""
    calls_1m: int = 0          # 最近1分钟调用次数
    errors_1m: int = 0         # 最近1分钟错误次数
    avg_latency_1m: float = 0  # 最近1分钟平均延迟
    last_error_time: float = 0
    circuit_open: bool = False # 熔断开关


class SmartRouter:
    """智能路由器"""
    
    def __init__(self):
        # LLM 供应商配置
        self.llm_providers: dict[str, ProviderConfig] = {
            "qwen": ProviderConfig(
                name="通义千问", 
                provider_id="qwen",
                priority=10, 
                cost_per_call=0.004, 
                avg_latency=1.5, 
                success_rate=0.99
            ),
            "deepseek": ProviderConfig(
                name="DeepSeek", 
                provider_id="deepseek",
                priority=8, 
                cost_per_call=0.002, 
                avg_latency=1.0, 
                success_rate=0.97
            ),
            "zhipu": ProviderConfig(
                name="智谱GLM", 
                provider_id="zhipu",
                priority=7, 
                cost_per_call=0.05, 
                avg_latency=2.0, 
                success_rate=0.98
            ),
            "mock": ProviderConfig(
                name="Mock", 
                provider_id="mock",
                priority=1, 
                cost_per_call=0, 
                avg_latency=0.5, 
                success_rate=1.0
            ),
        }
        
        # 图片生成供应商
        self.image_providers: dict[str, ProviderConfig] = {
            "wanx": ProviderConfig(
                name="通义万相", 
                provider_id="wanx",
                priority=10, 
                cost_per_call=0.1, 
                avg_latency=30, 
                success_rate=0.95
            ),
            "jimeng": ProviderConfig(
                name="即梦", 
                provider_id="jimeng",
                priority=8, 
                cost_per_call=0.15, 
                avg_latency=25, 
                success_rate=0.96
            ),
            "mock": ProviderConfig(
                name="Mock", 
                provider_id="mock",
                priority=1, 
                cost_per_call=0, 
                avg_latency=1, 
                success_rate=1.0
            ),
        }
        
        # 视频生成供应商
        self.video_providers: dict[str, ProviderConfig] = {
            "kling": ProviderConfig(
                name="可灵", 
                provider_id="kling",
                priority=10, 
                cost_per_call=0.5, 
                avg_latency=120, 
                success_rate=0.92
            ),
            "mock": ProviderConfig(
                name="Mock", 
                provider_id="mock",
                priority=1, 
                cost_per_call=0, 
                avg_latency=2, 
                success_rate=1.0
            ),
        }
        
        # TTS 供应商
        self.tts_providers: dict[str, ProviderConfig] = {
            "aliyun": ProviderConfig(
                name="阿里云TTS", 
                provider_id="aliyun",
                priority=10, 
                cost_per_call=0.02, 
                avg_latency=1, 
                success_rate=0.99
            ),
            "volcengine": ProviderConfig(
                name="火山引擎", 
                provider_id="volcengine",
                priority=8, 
                cost_per_call=0.02, 
                avg_latency=1.2, 
                success_rate=0.98
            ),
            "mock": ProviderConfig(
                name="Mock", 
                provider_id="mock",
                priority=1, 
                cost_per_call=0, 
                avg_latency=0.5, 
                success_rate=1.0
            ),
        }
        
        # 实时指标
        self._metrics: dict[str, ProviderMetrics] = {}
        
        # 轮询计数器
        self._round_robin_counters: dict[str, int] = {}
    
    def select_llm(
        self,
        strategy: RouteStrategy = RouteStrategy.BALANCED,
        exclude: list[str] = None,
        required_features: list[str] = None
    ) -> str:
        """选择 LLM 供应商"""
        return self._select_provider(
            self.llm_providers, 
            "llm", 
            strategy, 
            exclude
        )
    
    def select_image(
        self, 
        strategy: RouteStrategy = RouteStrategy.BALANCED, 
        exclude: list[str] = None
    ) -> str:
        """选择图片生成供应商"""
        return self._select_provider(
            self.image_providers, 
            "image", 
            strategy, 
            exclude
        )
    
    def select_video(
        self, 
        strategy: RouteStrategy = RouteStrategy.BALANCED, 
        exclude: list[str] = None
    ) -> str:
        """选择视频生成供应商"""
        return self._select_provider(
            self.video_providers, 
            "video", 
            strategy, 
            exclude
        )
    
    def select_tts(
        self, 
        strategy: RouteStrategy = RouteStrategy.BALANCED, 
        exclude: list[str] = None
    ) -> str:
        """选择 TTS 供应商"""
        return self._select_provider(
            self.tts_providers, 
            "tts", 
            strategy, 
            exclude
        )
    
    def _select_provider(
        self,
        providers: dict[str, ProviderConfig],
        provider_type: str,
        strategy: RouteStrategy,
        exclude: list[str] = None
    ) -> str:
        """通用选择逻辑"""
        exclude = exclude or []
        
        # 过滤可用供应商
        available = {
            k: v for k, v in providers.items()
            if v.is_available and k not in exclude and not self._is_circuit_open(f"{provider_type}:{k}")
        }
        
        if not available:
            # 尝试使用 mock
            if "mock" in providers and "mock" not in exclude:
                logger.warning(f"no_available_{provider_type}_provider", fallback="mock")
                return "mock"
            raise RuntimeError(f"没有可用的 {provider_type} 供应商")
        
        # 根据策略选择
        if strategy == RouteStrategy.COST:
            selected = min(available.items(), key=lambda x: x[1].cost_per_call)[0]
        
        elif strategy == RouteStrategy.QUALITY:
            selected = max(
                available.items(), 
                key=lambda x: x[1].priority * x[1].success_rate
            )[0]
        
        elif strategy == RouteStrategy.FASTEST:
            selected = min(available.items(), key=lambda x: x[1].avg_latency)[0]
        
        elif strategy == RouteStrategy.ROUND_ROBIN:
            selected = self._round_robin_select(available, provider_type)
        
        else:  # BALANCED
            selected = self._balanced_select(available)
        
        logger.debug(
            "provider_selected",
            type=provider_type,
            provider=selected,
            strategy=strategy.value
        )
        
        return selected
    
    def _balanced_select(self, providers: dict[str, ProviderConfig]) -> str:
        """综合评分选择"""
        def score(p: ProviderConfig) -> float:
            # 优先级权重 40%
            priority_score = p.priority / 10 * 0.4
            
            # 成本权重 30% (反向，成本越低越好)
            max_cost = max(x.cost_per_call for x in providers.values()) or 1
            cost_score = (1 - p.cost_per_call / max_cost) * 0.3
            
            # 成功率权重 20%
            success_score = p.success_rate * 0.2
            
            # 延迟权重 10% (反向)
            max_latency = max(x.avg_latency for x in providers.values()) or 1
            latency_score = (1 - p.avg_latency / max_latency) * 0.1
            
            return priority_score + cost_score + success_score + latency_score
        
        return max(providers.items(), key=lambda x: score(x[1]))[0]
    
    def _round_robin_select(
        self, 
        providers: dict[str, ProviderConfig], 
        provider_type: str
    ) -> str:
        """轮询选择"""
        counter_key = provider_type
        if counter_key not in self._round_robin_counters:
            self._round_robin_counters[counter_key] = 0
        
        provider_list = list(providers.keys())
        index = self._round_robin_counters[counter_key] % len(provider_list)
        self._round_robin_counters[counter_key] += 1
        
        return provider_list[index]
    
    # ==================== 健康管理 ====================
    
    def mark_success(
        self, 
        provider_type: str, 
        provider_name: str, 
        latency: float
    ):
        """标记调用成功"""
        key = f"{provider_type}:{provider_name}"
        
        # 更新配置
        providers = self._get_providers(provider_type)
        if provider_name in providers:
            p = providers[provider_name]
            p.total_calls += 1
            p.total_latency += latency
            p.failure_count = 0
            # 更新平均延迟 (移动平均)
            p.avg_latency = p.avg_latency * 0.9 + latency * 0.1
        
        # 更新指标
        metrics = self._get_metrics(key)
        metrics.calls_1m += 1
        metrics.avg_latency_1m = (metrics.avg_latency_1m * 0.9 + latency * 0.1)
    
    def mark_failure(self, provider_type: str, provider_name: str, error: str = None):
        """标记调用失败"""
        key = f"{provider_type}:{provider_name}"
        
        providers = self._get_providers(provider_type)
        if provider_name in providers:
            p = providers[provider_name]
            p.failure_count += 1
            p.total_calls += 1
            # 更新成功率
            if p.total_calls > 0:
                p.success_rate = 1 - (p.failure_count / p.total_calls)
        
        metrics = self._get_metrics(key)
        metrics.errors_1m += 1
        metrics.last_error_time = time.time()
        
        # 熔断检查
        if metrics.errors_1m >= 5:
            metrics.circuit_open = True
            logger.warning(
                "circuit_breaker_opened",
                provider_type=provider_type,
                provider=provider_name,
                error=error
            )
    
    def mark_unavailable(self, provider_type: str, provider_name: str):
        """标记供应商不可用"""
        providers = self._get_providers(provider_type)
        if provider_name in providers:
            providers[provider_name].is_available = False
            logger.warning(f"{provider_type}_provider_unavailable", provider=provider_name)
    
    def mark_available(self, provider_type: str, provider_name: str):
        """标记供应商可用"""
        providers = self._get_providers(provider_type)
        if provider_name in providers:
            providers[provider_name].is_available = True
            # 重置熔断
            key = f"{provider_type}:{provider_name}"
            if key in self._metrics:
                self._metrics[key].circuit_open = False
                self._metrics[key].errors_1m = 0
    
    def _is_circuit_open(self, key: str) -> bool:
        """检查熔断器状态"""
        if key not in self._metrics:
            return False
        
        metrics = self._metrics[key]
        
        # 熔断后 60 秒尝试恢复
        if metrics.circuit_open:
            if time.time() - metrics.last_error_time > 60:
                metrics.circuit_open = False
                metrics.errors_1m = 0
                return False
            return True
        
        return False
    
    def _get_providers(self, provider_type: str) -> dict[str, ProviderConfig]:
        """获取供应商字典"""
        return getattr(self, f"{provider_type}_providers", {})
    
    def _get_metrics(self, key: str) -> ProviderMetrics:
        """获取供应商指标"""
        if key not in self._metrics:
            self._metrics[key] = ProviderMetrics()
        return self._metrics[key]
    
    # ==================== 统计信息 ====================
    
    def get_stats(self) -> dict:
        """获取路由统计"""
        stats = {}
        
        for provider_type in ["llm", "image", "video", "tts"]:
            providers = self._get_providers(provider_type)
            stats[provider_type] = {}
            
            for name, config in providers.items():
                key = f"{provider_type}:{name}"
                metrics = self._metrics.get(key, ProviderMetrics())
                
                stats[provider_type][name] = {
                    "name": config.name,
                    "is_available": config.is_available,
                    "priority": config.priority,
                    "cost_per_call": config.cost_per_call,
                    "avg_latency": round(config.avg_latency, 2),
                    "success_rate": round(config.success_rate, 4),
                    "total_calls": config.total_calls,
                    "circuit_open": metrics.circuit_open,
                    "errors_1m": metrics.errors_1m
                }
        
        return stats


# 全局实例
_smart_router: SmartRouter = None


def get_smart_router() -> SmartRouter:
    """获取智能路由器实例"""
    global _smart_router
    if _smart_router is None:
        _smart_router = SmartRouter()
    return _smart_router

