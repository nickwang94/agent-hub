"""
LLM 客户端封装

提供统一的 LLM 访问接口，支持不同的模型提供商
"""
from langchain_openai import ChatOpenAI
from core.config import Config


def create_llm(streaming: bool = False):
    """
    创建 LLM 实例

    阿里百炼兼容 OpenAI API 格式，使用 ChatOpenAI 即可访问

    Args:
        streaming: 是否启用流式输出

    Returns:
        ChatOpenAI: LLM 实例
    """
    # 阿里百炼 API 配置
    # 使用阿里云百炼兼容 OpenAI 接口端点
    base_url = Config.LLM_BASE_URL or "https://coding.dashscope.aliyuncs.com/v1"

    return ChatOpenAI(
        model=Config.LLM_MODEL,
        api_key=Config.DASHSCOPE_API_KEY,
        base_url=base_url,
        temperature=0.7,
        streaming=streaming,
        max_tokens=4096,
    )


# 全局 LLM 实例（可选，用于共享）
_llm_instance = None


def get_llm(streaming: bool = False):
    """获取全局 LLM 实例"""
    global _llm_instance
    if _llm_instance is None or streaming:
        _llm_instance = create_llm(streaming)
    return _llm_instance
