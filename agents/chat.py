"""
对话 Agent

用于普通对话交互，是最基础的 Agent 类型
"""
from typing import List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from .base import BaseAgent
from core.llm import create_llm


class ChatAgent(BaseAgent):
    """
    对话 Agent

    处理通用的对话交互，保持对话连贯性
    """

    DEFAULT_SYSTEM_PROMPT = """你是一个友好的 AI 助手。
请用简洁、清晰的方式回答用户的问题。
如果不确定答案，请诚实地告诉用户。"""

    def __init__(
        self,
        name: str = "ChatAgent",
        description: str = "通用对话助手",
        system_prompt: Optional[str] = None,
    ):
        """
        初始化对话 Agent

        Args:
            name: Agent 名称
            description: Agent 描述
            system_prompt: 系统提示词
        """
        super().__init__(name, description)
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.llm = create_llm()

    def invoke(
        self, message: str, context: Optional[List[BaseMessage]] = None
    ) -> str:
        """
        处理用户对话请求

        Args:
            message: 用户输入
            context: 对话历史上下文

        Returns:
            str: 对话响应
        """
        # 构建消息列表
        messages: List[BaseMessage] = []

        # 添加系统提示
        messages.append(SystemMessage(content=self.system_prompt))

        # 添加上下文
        if context:
            messages.extend(context)

        # 添加当前用户消息
        messages.append(HumanMessage(content=message))

        # 调用 LLM
        response = self.llm.invoke(messages)

        return response.content

    def stream_invoke(
        self, message: str, context: Optional[List[BaseMessage]] = None
    ):
        """
        流式处理用户请求

        Args:
            message: 用户输入
            context: 对话历史上下文

        Yields:
            str: 流式响应片段
        """
        messages: List[BaseMessage] = []
        messages.append(SystemMessage(content=self.system_prompt))

        if context:
            messages.extend(context)

        messages.append(HumanMessage(content=message))

        # 流式调用
        for chunk in self.llm.stream(messages):
            if chunk.content:
                yield chunk.content
