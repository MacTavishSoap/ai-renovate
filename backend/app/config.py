"""配置加载 — 全部走环境变量，不硬编码"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """从环境变量 / .env 文件加载配置"""

    # 图像生成 API
    image_api_base_url: str = "https://api.smile-ai-studio.com/v1"
    image_api_key: str = ""
    image_model: str = "gpt-image-2"

    # LLM API（Pydantic AI Agent）
    llm_api_base_url: str = "https://api.smile-ai-studio.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"

    # 数据库
    database_url: str = "sqlite:///./data/app.db"

    # 应用
    app_env: str = "development"
    app_secret_key: str = "change-me-in-production"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
