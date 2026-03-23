"""
Base Agent Class

Defines common interface and behavior for all agents
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class BaseAgent(ABC):
    """
    Base Agent abstract class

    All specific agents must inherit from this class and implement related methods
    """

    def __init__(self, name: str, description: str = ""):
        """
        Initialize base agent

        Args:
            name: Agent name
            description: Agent description
        """
        self.name = name
        self.description = description
        self._memory: List[BaseMessage] = []

    @abstractmethod
    def invoke(self, message: str, context: Optional[List[BaseMessage]] = None) -> str:
        """
        Process user input and return response

        Args:
            message: User input
            context: Optional conversation history context

        Returns:
            str: Agent response
        """
        pass

    def add_to_memory(self, message: BaseMessage):
        """Add message to memory"""
        self._memory.append(message)

    def clear_memory(self):
        """Clear memory"""
        self._memory = []

    def get_memory(self) -> List[BaseMessage]:
        """Get messages from memory"""
        return self._memory.copy()

    def get_state(self) -> Dict[str, Any]:
        """Get agent current state"""
        return {
            "name": self.name,
            "description": self.description,
            "memory_length": len(self._memory),
        }
