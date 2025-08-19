"""Telegram session domain entity."""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class SessionStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALID = "invalid"


@dataclass(frozen=True)
class SessionId:
    """Value object for Session ID."""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Session ID cannot be empty")


@dataclass(frozen=True)
class TelegramCredentials:
    """Value object for Telegram API credentials."""
    api_id: int
    api_hash: str
    
    def __post_init__(self):
        if not self.api_id or self.api_id <= 0:
            raise ValueError("API ID must be positive integer")
        if not self.api_hash or len(self.api_hash.strip()) == 0:
            raise ValueError("API Hash cannot be empty")


@dataclass
class TelegramUser:
    """Telegram user information."""
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class TelegramSession:
    """Telegram session domain entity."""
    
    id: SessionId
    user_id: str
    phone_number: str
    credentials: TelegramCredentials
    encrypted_session_data: str
    telegram_user: Optional[TelegramUser] = None
    status: SessionStatus = SessionStatus.ACTIVE
    last_used_at: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def is_valid(self) -> bool:
        """Check if session is valid and active."""
        return self.status == SessionStatus.ACTIVE
    
    def mark_as_used(self) -> None:
        """Mark session as recently used."""
        self.last_used_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def expire(self) -> None:
        """Mark session as expired."""
        self.status = SessionStatus.EXPIRED
        self.updated_at = datetime.utcnow()
    
    def invalidate(self) -> None:
        """Mark session as invalid."""
        self.status = SessionStatus.INVALID
        self.updated_at = datetime.utcnow()
    
    def update_telegram_user(self, telegram_user: TelegramUser) -> None:
        """Update Telegram user information."""
        self.telegram_user = telegram_user
        self.updated_at = datetime.utcnow()