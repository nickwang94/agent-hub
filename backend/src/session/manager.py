"""
Session Management Module

Manages user session state and conversation history
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
    Session class

    Stores state and history for a single session
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    messages: List[BaseMessage] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str):
        """
        Add message to session

        Args:
            role: Role (user/assistant)
            content: Message content
        """
        if role == "user":
            self.messages.append(HumanMessage(content=content))
        elif role == "assistant":
            self.messages.append(AIMessage(content=content))

        self.updated_at = time.time()

        # Limit message count
        if len(self.messages) > Config.MAX_SESSION_MESSAGES:
            # Keep latest messages, remove earliest
            self.messages = self.messages[-Config.MAX_SESSION_MESSAGES:]

    def get_messages(self) -> List[BaseMessage]:
        """Get all messages"""
        return self.messages.copy()

    def get_last_n_messages(self, n: int) -> List[BaseMessage]:
        """Get last N messages"""
        return self.messages[-n:]

    def clear(self):
        """Clear session history"""
        self.messages = []
        self.updated_at = time.time()

    def is_expired(self) -> bool:
        """Check if session is expired"""
        elapsed = time.time() - self.updated_at
        return elapsed > (Config.SESSION_EXPIRE_MINUTES * 60)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
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
    Session manager

    Manages lifecycle of multiple sessions
    """

    def __init__(self):
        """Initialize session manager"""
        self._sessions: Dict[str, Session] = {}

    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> Session:
        """
        Create new session

        Args:
            metadata: Session metadata

        Returns:
            Session: Newly created session
        """
        session = Session()
        if metadata:
            session.metadata = metadata
        self._sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session

        Args:
            session_id: Session ID

        Returns:
            Optional[Session]: Session object, or None if not exists or expired
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
        Delete session

        Args:
            session_id: Session ID

        Returns:
            bool: Whether deletion was successful
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def get_or_create_session(
        self, session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """
        Get or create session

        Args:
            session_id: Session ID, if None create new session
            metadata: Metadata (only used when creating new session)

        Returns:
            Session: Session object
        """
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session

        return self.create_session(metadata)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        self._cleanup_expired()
        return [s.to_dict() for s in self._sessions.values()]

    def _cleanup_expired(self):
        """Clean up expired sessions"""
        expired = [
            sid for sid, s in self._sessions.items() if s.is_expired()
        ]
        for sid in expired:
            del self._sessions[sid]

    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        self._cleanup_expired()
        return {
            "total_sessions": len(self._sessions),
            "total_messages": sum(len(s.messages) for s in self._sessions.values()),
        }
