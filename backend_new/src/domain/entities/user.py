"""User domain entity with business logic."""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum


class SubscriptionType(Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass(frozen=True)
class UserId:
    """Value object for User ID."""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("User ID cannot be empty")


@dataclass
class User:
    """User domain entity with rich business logic."""
    
    id: UserId
    username: str
    email: str
    password_hash: str
    full_name: str
    status: UserStatus = UserStatus.ACTIVE
    is_admin: bool = False
    subscription_type: SubscriptionType = SubscriptionType.FREE
    subscription_expires: Optional[datetime] = None
    api_token: Optional[str] = None
    telegram_sessions: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.telegram_sessions is None:
            self.telegram_sessions = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def is_subscription_active(self) -> bool:
        """Check if user subscription is active."""
        if self.subscription_type == SubscriptionType.FREE:
            return True
        
        if self.subscription_expires:
            return self.subscription_expires > datetime.utcnow()
        
        return False
    
    def can_add_groups(self, current_groups: int) -> bool:
        """Check if user can add more groups based on subscription."""
        limits = {
            SubscriptionType.FREE: 5,
            SubscriptionType.PREMIUM: 50,
            SubscriptionType.ENTERPRISE: 999
        }
        
        max_groups = limits.get(self.subscription_type, 5)
        return current_groups < max_groups
    
    def can_send_messages(self, daily_messages: int) -> bool:
        """Check if user can send more messages today."""
        limits = {
            SubscriptionType.FREE: 50,
            SubscriptionType.PREMIUM: 500,
            SubscriptionType.ENTERPRISE: 9999
        }
        
        max_messages = limits.get(self.subscription_type, 50)
        return daily_messages < max_messages
    
    def add_telegram_session(self, session_id: str) -> None:
        """Add a Telegram session to user."""
        if session_id not in self.telegram_sessions:
            self.telegram_sessions.append(session_id)
            self.updated_at = datetime.utcnow()
    
    def remove_telegram_session(self, session_id: str) -> None:
        """Remove a Telegram session from user."""
        if session_id in self.telegram_sessions:
            self.telegram_sessions.remove(session_id)
            self.updated_at = datetime.utcnow()
    
    def upgrade_subscription(self, new_type: SubscriptionType, expires_at: datetime) -> None:
        """Upgrade user subscription."""
        self.subscription_type = new_type
        self.subscription_expires = expires_at
        self.updated_at = datetime.utcnow()
    
    def suspend(self) -> None:
        """Suspend user account."""
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate user account."""
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.utcnow()