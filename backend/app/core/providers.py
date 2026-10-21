"""Provider 抽象层 — 支持多 Provider 主备切换

设计：
- 每个能力（LLM/Image/SR/Storage）可配置多个 Provider
- 按 priority 排序，优先用高优先级的
- 失败时自动降级到下一个
- 支持按任务类型选择不同 Provider
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

import httpx

from ..config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ProviderType(Enum := __import__("enum").Enum):
    """Provider 类型"""
    LLM = "llm"
    IMAGE = "image"
    SR = "sr"
    STORAGE = "storage"


@dataclass
class ProviderEndpoint:
    """单个 Provider 配置"""
    name: str                    # e.g. "doubao", "gpt-4o", "wanxiang"
    base_url: str
    api_key: str
    model: str | None = None
    priority: int = 0            # 越大越优先
    enabled: bool = True
    timeout: float = 120.0
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderSet:
    """同类 Provider 集合（支持多备选）"""
    provider_type: ProviderType
    endpoints: list[ProviderEndpoint] = field(default_factory=list)

    def get_primary(self) -> ProviderEndpoint | None:
        """获取最高优先级且启用的 Provider"""
        candidates = [e for e in self.endpoints if e.enabled]
        if not candidates:
            return None
        return max(candidates, key=lambda e: e.priority)

    def get_next(self, current: str) -> ProviderEndpoint | None:
        """获取当前 Provider 的下一个备选"""
        candidates = [e for e in self.endpoints if e.enabled and e.name != current]
        if not candidates:
            return None
        return max(candidates, key=lambda e: e.priority)


class BaseProvider(ABC, Generic[T]):
    """Provider 抽象基类"""

    def __init__(self, endpoint: ProviderEndpoint):
        self.endpoint = endpoint
        self.name = endpoint.name
        self.base_url = endpoint.base_url
        self.api_key = endpoint.api_key
        self.model = endpoint.model
        self.timeout = endpoint.timeout

    @abstractmethod
    async def call(self, **kwargs) -> T:
        """调用 Provider"""
        pass

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(f"{self.base_url}/models")
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"[{self.name}] health check failed: {e}")
            return False


class LLMProvider(BaseProvider):
    """LLM Provider — 支持主备切换"""
    provider_type = ProviderType.LLM

    async def call(self, prompt: str, **kwargs) -> str:
        """调用 LLM，返回文本"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]


class ImageProvider(BaseProvider):
    """图像生成 Provider"""
    provider_type = ProviderType.IMAGE

    async def call(self, prompt: str, **kwargs) -> dict:
        """调用图像生成 API，返回 {b64_json, url}"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            **kwargs,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/images/generations", headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()["data"][0]


# ===== Provider 容器 =====

class ProviderRegistry:
    """全局 Provider 注册表"""

    def __init__(self):
        self._sets: dict[ProviderType, ProviderSet] = {}
        self._instances: dict[str, BaseProvider] = {}

    def register_set(self, provider_set: ProviderSet):
        self._sets[provider_set.provider_type] = provider_set

    def get_provider(self, provider_type: ProviderType) -> BaseProvider | None:
        """获取当前最高优先级 Provider（自动实例化）"""
        pset = self._sets.get(provider_type)
        if not pset:
            return None
        endpoint = pset.get_primary()
        if not endpoint:
            return None
        return self._get_or_create(endpoint, provider_type)

    def get_next_provider(self, provider_type: ProviderType, current_name: str) -> BaseProvider | None:
        """获取当前 Provider 的下一个备选"""
        pset = self._sets.get(provider_type)
        if not pset:
            return None
        endpoint = pset.get_next(current_name)
        if not endpoint:
            return None
        return self._get_or_create(endpoint, provider_type)

    def _get_or_create(self, endpoint: ProviderEndpoint, provider_type: ProviderType) -> BaseProvider:
        key = f"{provider_type.value}:{endpoint.name}"
        if key not in self._instances:
            cls = _PROVIDER_CLASSES.get(provider_type)
            if cls:
                self._instances[key] = cls(endpoint)
            else:
                raise ValueError(f"Unknown provider type: {provider_type}")
        return self._instances[key]

    def with_fallback(self, provider_type: ProviderType):
        """返回带降级逻辑的 Provider（自动尝试备选）"""
        return _FallbackProvider(self, provider_type)


_PROVIDER_CLASSES: dict[ProviderType, type[BaseProvider]] = {
    ProviderType.LLM: LLMProvider,
    ProviderType.IMAGE: ImageProvider,
}


class _FallbackProvider:
    """带降级的 Provider 包装器"""

    def __init__(self, registry: ProviderRegistry, provider_type: ProviderType):
        self.registry = registry
        self.provider_type = provider_type

    async def call(self, **kwargs) -> Any:
        """依次尝试各 Provider，直到成功"""
        provider = self.registry.get_provider(self.provider_type)
        tried: list[str] = []

        while provider:
            tried.append(provider.name)
            try:
                return await provider.call(**kwargs)
            except Exception as e:
                logger.warning(f"[{provider.name}] call failed: {e}, trying fallback...")
                provider = self.registry.get_next_provider(self.provider_type, provider.name)

        raise RuntimeError(f"All providers failed for {self.provider_type.value}, tried: {tried}")


# ===== 全局单例 =====
_registry: ProviderRegistry | None = None


def get_registry() -> ProviderRegistry:
    global _registry
    if _registry is None:
        _registry = _init_registry()
    return _registry


def _init_registry() -> ProviderRegistry:
    """从 config 初始化注册表"""
    reg = ProviderRegistry()

    # LLM Providers
    llm_set = ProviderSet(provider_type=ProviderType.LLM)
    # 从 config 读取多 provider 配置
    llm_endpoints = getattr(settings, "llm_providers", [])
    for ep in llm_endpoints:
        llm_set.endpoints.append(ProviderEndpoint(**ep))
    if llm_set.endpoints:
        reg.register_set(llm_set)

    # Image Providers
    img_set = ProviderSet(provider_type=ProviderType.IMAGE)
    img_endpoints = getattr(settings, "image_providers", [])
    for ep in img_endpoints:
        img_set.endpoints.append(ProviderEndpoint(**ep))
    if img_set.endpoints:
        reg.register_set(img_set)

    return reg


# ===== 便捷方法 =====

async def call_llm(prompt: str, **kwargs) -> str:
    """调用 LLM，自动降级"""
    return await get_registry().with_fallback(ProviderType.LLM).call(prompt=prompt, **kwargs)


async def call_image(prompt: str, **kwargs) -> dict:
    """调用图像生成，自动降级"""
    return await get_registry().with_fallback(ProviderType.IMAGE).call(prompt=prompt, **kwargs)
