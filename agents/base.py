"""
基础 Agent 类

定义所有 Agent 的通用接口和行为
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class BaseAgent(ABC):
    """
    基础 Agent 抽象类

    所有具体的 Agent 都需要继承此类并实现相关方法
    """

    def __init__(self, name: str, description: str = ""):
        """
        初始化基础 Agent

        Args:
            name: Agent 名称
            description: Agent 描述
        """
        self.name = name
        self.description = description
        self._memory: List[BaseMessage] = []

    @abstractmethod
    def invoke(self, message: str, context: Optional[List[BaseMessage]] = None) -> str:
        """
        处理用户输入并返回响应

        Args:
            message: 用户输入
            context: 可选的对话历史上下文

        Returns:
            str: Agent 的响应
        """
        pass

    def add_to_memory(self, message: BaseMessage):
        """添加消息到内存"""
        self._memory.append(message)

    def clear_memory(self):
        """清空内存"""
        self._memory = []

    def get_memory(self) -> List[BaseMessage]:
        """获取内存中的消息"""
        return self._memory.copy()

    def get_state(self) -> Dict[str, Any]:
        """获取 Agent 当前状态"""
        return {
            "name": self.name,
            "description": self.description,
            "memory_length": len(self._memory),
        }
