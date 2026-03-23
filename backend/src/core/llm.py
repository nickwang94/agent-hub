"""
LLM Client Wrapper

Provides unified LLM access interface, supports different model providers
"""
from langchain_openai import ChatOpenAI
from core.config import Config


def create_llm(streaming: bool = False):
    """
    Create LLM instance

    Alibaba DashScope is compatible with OpenAI API format, uses ChatOpenAI for access

    Args:
        streaming: Whether to enable streaming output

    Returns:
        ChatOpenAI: LLM instance
    """
    # Alibaba DashScope API Configuration
    # Use Alibaba DashScope compatible OpenAI interface endpoint
    base_url = Config.LLM_BASE_URL or "https://coding.dashscope.aliyuncs.com/v1"

    return ChatOpenAI(
        model=Config.LLM_MODEL,
        api_key=Config.DASHSCOPE_API_KEY,
        base_url=base_url,
        temperature=0.7,
        streaming=streaming,
        max_tokens=4096,
    )


# Global LLM instance (optional, for sharing)
_llm_instance = None


def get_llm(streaming: bool = False):
    """Get global LLM instance"""
    global _llm_instance
    if _llm_instance is None or streaming:
        _llm_instance = create_llm(streaming)
    return _llm_instance
