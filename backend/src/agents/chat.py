"""
Chat Agent

Used for conversational interaction, the most basic agent type
"""
from typing import List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from .base import BaseAgent
from core.llm import create_llm


class ChatAgent(BaseAgent):
    """
    Chat Agent

    Handles general conversational interaction, maintains conversation continuity
    """

    DEFAULT_SYSTEM_PROMPT = """You are a friendly AI assistant.
Please answer user questions in a concise and clear manner.
If you are unsure of the answer, please honestly tell the user."""

    def __init__(
        self,
        name: str = "ChatAgent",
        description: str = "General conversation assistant",
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize chat agent

        Args:
            name: Agent name
            description: Agent description
            system_prompt: System prompt
        """
        super().__init__(name, description)
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        self.llm = create_llm()

    def invoke(
        self, message: str, context: Optional[List[BaseMessage]] = None
    ) -> str:
        """
        Process user conversation request

        Args:
            message: User input
            context: Conversation history context

        Returns:
            str: Conversation response
        """
        # Build message list
        messages: List[BaseMessage] = []

        # Add system prompt
        messages.append(SystemMessage(content=self.system_prompt))

        # Add context
        if context:
            messages.extend(context)

        # Add current user message
        messages.append(HumanMessage(content=message))

        # Call LLM
        response = self.llm.invoke(messages)

        return response.content

    def stream_invoke(
        self, message: str, context: Optional[List[BaseMessage]] = None
    ):
        """
        Stream process user request

        Args:
            message: User input
            context: Conversation history context

        Yields:
            str: Stream response chunks
        """
        messages: List[BaseMessage] = []
        messages.append(SystemMessage(content=self.system_prompt))

        if context:
            messages.extend(context)

        messages.append(HumanMessage(content=message))

        # Stream call
        for chunk in self.llm.stream(messages):
            if chunk.content:
                yield chunk.content
