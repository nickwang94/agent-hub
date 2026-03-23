"""
Configuration Management Module

Manages environment variables using dotenv, provides unified configuration access
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


class Config:
    """Configuration management class"""

    # LLM Configuration - Alibaba DashScope
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")

    # Alibaba DashScope API Base URL (optional, for custom endpoint)
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")

    # Knowledge base configuration
    CHROMA_PERSIST_DIR = os.getenv(
        "CHROMA_PERSIST_DIR",
        str(Path(__file__).parent.parent.parent / "data/chroma_db")
    )

    # Session configuration
    SESSION_EXPIRE_MINUTES = 30
    MAX_SESSION_MESSAGES = 100

    @classmethod
    def validate(cls) -> bool:
        """Validate that required configurations exist"""
        if not cls.DASHSCOPE_API_KEY:
            raise ValueError("DASHSCOPE_API_KEY environment variable not set")
        return True
