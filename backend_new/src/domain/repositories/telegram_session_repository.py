"""Telegram session repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.telegram_session import TelegramSession, SessionId


class TelegramSessionRepository(ABC):
    """Abstract telegram session repository interface."""
    
    @abstractmethod
    async def save(self, session: TelegramSession) -> None:
        """Save session to database."""
        pass
    
    @abstractmethod
    async def find_by_id(self, session_id: SessionId) -> Optional[TelegramSession]:
        """Find session by ID."""
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[TelegramSession]:
        """Find sessions by user ID."""
        pass
    
    @abstractmethod
    async def find_by_phone_number(self, phone_number: str) -> Optional[TelegramSession]:
        """Find session by phone number."""
        pass
    
    @abstractmethod
    async def list_active_sessions(self) -> List[TelegramSession]:
        """List all active sessions."""
        pass
    
    @abstractmethod
    async def delete(self, session_id: SessionId) -> bool:
        """Delete session."""
        pass
    
    @abstractmethod
    async def count_by_user(self, user_id: str) -> int:
        """Count sessions by user."""
        pass