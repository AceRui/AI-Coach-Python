import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    """应用配置类"""

    # 加载环境变量
    load_dotenv()

    ENV_PATH: Path = Path(__file__).resolve().parents[1] / ".env"

    # LLM配置
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_MODEL: str = os.getenv("GOOGLE_MODEL", "")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "")

    # Redis配置
    REDIS_DATABASE_URL: str = os.getenv("REDIS_DATABASE_URL", "redis://localhost:6379")
    REDIS_MEMORY_TTL: int = int(os.getenv("REDIS_MEMORY_TTL", 3600))  # 短期记忆默认保存1小时
    SHORT_MEMORY_DB_NAME: str = os.getenv("SHORT_MEMORY_DB_NAME", "")


# 创建全局配置实例
settings = Settings()
