"""配置加载 — 支持 config.json + 环境变量双通道，不硬编码"""

import json
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings


def _load_config_json() -> dict:
    """从 config.json 读取配置"""
    candidates = [
        Path(__file__).resolve().parent.parent / "config.json",
        Path(__file__).resolve().parent.parent.parent / "config.json",
    ]
    for p in candidates:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}


_cfg = _load_config_json()


class Settings(BaseSettings):
    """优先级：环境变量 > config.json > 默认值"""

    # ===== 多 Provider 配置 =====
    # 格式: { "llm": [{"name": "doubao", "base_url": ..., "api_key": ..., "model": ..., "priority": 10}], ... }
    llm_providers: list[dict] = _cfg.get("providers", {}).get("llm", [])
    image_providers: list[dict] = _cfg.get("providers", {}).get("image", [])
    sr_providers: list[dict] = _cfg.get("providers", {}).get("sr", [])
    storage_providers: list[dict] = _cfg.get("providers", {}).get("storage", [])

    # ===== 向后兼容：单个 Provider 配置 =====
    # 如果 providers.* 未配置，回退到这些字段
    image_api_base_url: str = _cfg.get("image_api", {}).get("base_url", "https://api.smile-ai-studio.com/v1")
    image_api_key: str = _cfg.get("image_api", {}).get("api_key", "")
    image_model: str = _cfg.get("image_api", {}).get("model", "gpt-image-2")
    image_default_quality: str = _cfg.get("image_api", {}).get("default_quality", "high")
    image_default_size: str = _cfg.get("image_api", {}).get("default_size", "1024x1024")

    llm_api_base_url: str = _cfg.get("llm_api", {}).get("base_url", "https://api.smile-ai-studio.com/v1")
    llm_api_key: str = _cfg.get("llm_api", {}).get("api_key", "")
    llm_model: str = _cfg.get("llm_api", {}).get("model", "gpt-4o-mini")

    # ===== 短信 =====
    sms_access_key_id: str = _cfg.get("aliyun_sms", {}).get("access_key_id", "")
    sms_access_key_secret: str = _cfg.get("aliyun_sms", {}).get("access_key_secret", "")
    sms_sign_name: str = _cfg.get("aliyun_sms", {}).get("sign_name", "")
    sms_template_code: str = _cfg.get("aliyun_sms", {}).get("template_code", "")

    # ===== 阿里云超分 =====
    sr_access_key_id: str = _cfg.get("aliyun_super_res", {}).get("access_key_id", "")
    sr_access_key_secret: str = _cfg.get("aliyun_super_res", {}).get("access_key_secret", "")

    # ===== 火山引擎 =====
    volcengine_api_key: str = _cfg.get("volcengine", {}).get("api_key", "")
    volcengine_endpoint: str = _cfg.get("volcengine", {}).get("endpoint", "https://mediakit.cn-beijing.volces.com")

    # ===== 腾讯云 COS =====
    cos_secret_id: str = _cfg.get("tencent_cos", {}).get("secret_id", "")
    cos_secret_key: str = _cfg.get("tencent_cos", {}).get("secret_key", "")
    cos_bucket: str = _cfg.get("tencent_cos", {}).get("bucket", "")
    cos_region: str = _cfg.get("tencent_cos", {}).get("region", "ap-guangzhou")

    # ===== 数据库 =====
    database_url: str = _cfg.get("database", {}).get("url", "sqlite:///./data/app.db")

    # ===== 超分 =====
    super_res_enabled: bool = _cfg.get("super_res", {}).get("enabled", False)
    super_res_default_scale: int = _cfg.get("super_res", {}).get("default_scale", 2)
    super_res_default_format: str = _cfg.get("super_res", {}).get("default_format", "jpg")
    super_res_default_quality: int = _cfg.get("super_res", {}).get("default_quality", 95)

    # ===== 应用 =====
    app_env: str = _cfg.get("app", {}).get("env", "development")
    app_secret_key: str = _cfg.get("app", {}).get("secret_key", "change-me-in-production")
    app_host: str = _cfg.get("app", {}).get("host", "0.0.0.0")
    app_port: int = _cfg.get("app", {}).get("port", 8000)

    # ===== Prompts =====
    prompts_global_suffix: str = _cfg.get("prompts", {}).get("global_suffix", "")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def get_primary_llm(self) -> dict | None:
        """获取最高优先级 LLM Provider"""
        if not self.llm_providers:
            return None
        enabled = [p for p in self.llm_providers if p.get("enabled", True)]
        if not enabled:
            return None
        return max(enabled, key=lambda p: p.get("priority", 0))

    def get_primary_image(self) -> dict | None:
        """获取最高优先级图像 Provider"""
        if not self.image_providers:
            return None
        enabled = [p for p in self.image_providers if p.get("enabled", True)]
        if not enabled:
            return None
        return max(enabled, key=lambda p: p.get("priority", 0))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
