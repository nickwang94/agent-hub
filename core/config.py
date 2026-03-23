"""
配置管理模块

使用 dotenv 管理环境变量，提供统一的配置访问接口
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Config:
    """配置管理类"""

    # LLM 配置 - 阿里百炼
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")

    # 阿里百炼 API Base URL (可选，如果使用自定义端点)
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")

    # 知识库配置
    CHROMA_PERSIST_DIR = os.getenv(
        "CHROMA_PERSIST_DIR",
        str(Path(__file__).parent.parent / "chroma_db")
    )

    # Session 配置
    SESSION_EXPIRE_MINUTES = 30
    MAX_SESSION_MESSAGES = 100

    @classmethod
    def validate(cls) -> bool:
        """验证必要的配置是否存在"""
        if not cls.DASHSCOPE_API_KEY:
            raise ValueError("DASHSCOPE_API_KEY 环境变量未设置")
        return True
