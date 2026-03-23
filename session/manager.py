"""
Session 管理模块

管理用户会话状态和对话历史
"""
import uuid
import time
from typing import Dict, List, Optional, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from dataclasses import dataclass, field
from core.config import Config


@dataclass
class Session:
    """
    会话类

    存储单个会话的状态和历史信息
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    messages: List[BaseMessage] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str):
        """
        添加消息到会话

        Args:
            role: 角色 (user/assistant)
            content: 消息内容
        """
        if role == "user":
            self.messages.append(HumanMessage(content=content))
        elif role == "assistant":
            self.messages.append(AIMessage(content=content))

        self.updated_at = time.time()

        # 限制消息数量
        if len(self.messages) > Config.MAX_SESSION_MESSAGES:
            # 保留最新的消息，移除最早的
            self.messages = self.messages[-Config.MAX_SESSION_MESSAGES :]

    def get_messages(self) -> List[BaseMessage]:
        """获取所有消息"""
        return self.messages.copy()

    def get_last_n_messages(self, n: int) -> List[BaseMessage]:
        """获取最近 N 条消息"""
        return self.messages[-n:]

    def clear(self):
        """清空会话历史"""
        self.messages = []
        self.updated_at = time.time()

    def is_expired(self) -> bool:
        """检查会话是否已过期"""
        elapsed = time.time() - self.updated_at
        return elapsed > (Config.SESSION_EXPIRE_MINUTES * 60)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [
                {"role": "user" if isinstance(m, HumanMessage) else "assistant", "content": m.content}
                for m in self.messages
            ],
            "metadata": self.metadata,
        }


class SessionManager:
    """
    会话管理器

    管理多个会话的生命周期
    """

    def __init__(self):
        """初始化会话管理器"""
        self._sessions: Dict[str, Session] = {}

    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> Session:
        """
        创建新会话

        Args:
            metadata: 会话元数据

        Returns:
            Session: 新创建的会话
        """
        session = Session()
        if metadata:
            session.metadata = metadata
        self._sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        获取会话

        Args:
            session_id: 会话 ID

        Returns:
            Optional[Session]: 会话对象，如果不存在或已过期则返回 None
        """
        session = self._sessions.get(session_id)

        if session is None:
            return None

        if session.is_expired():
            self.delete_session(session_id)
            return None

        return session

    def delete_session(self, session_id: str) -> bool:
        """
        删除会话

        Args:
            session_id: 会话 ID

        Returns:
            bool: 是否成功删除
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def get_or_create_session(
        self, session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """
        获取或创建会话

        Args:
            session_id: 会话 ID，如果 None 则创建新会话
            metadata: 元数据（仅在创建新会话时使用）

        Returns:
            Session: 会话对象
        """
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session

        return self.create_session(metadata)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有活跃会话"""
        self._cleanup_expired()
        return [s.to_dict() for s in self._sessions.values()]

    def _cleanup_expired(self):
        """清理过期会话"""
        expired = [
            sid for sid, s in self._sessions.items() if s.is_expired()
        ]
        for sid in expired:
            del self._sessions[sid]

    def get_stats(self) -> Dict[str, Any]:
        """获取会话统计信息"""
        self._cleanup_expired()
        return {
            "total_sessions": len(self._sessions),
            "total_messages": sum(len(s.messages) for s in self._sessions.values()),
        }
