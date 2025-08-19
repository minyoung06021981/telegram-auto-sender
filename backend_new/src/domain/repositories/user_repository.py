"""User repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.user import User, UserId, SubscriptionType


class UserRepository(ABC):
    """Abstract user repository interface."""
    
    @abstractmethod
    async def save(self, user: User) -> None:
        """Save user to database."""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find user by ID."""
        pass
    
    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username."""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        pass
    
    @abstractmethod
    async def find_by_api_token(self, api_token: str) -> Optional[User]:
        """Find user by API token."""
        pass
    
    @abstractmethod
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination."""
        pass
    
    @abstractmethod
    async def count_by_subscription_type(self, subscription_type: SubscriptionType) -> int:
        """Count users by subscription type."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UserId) -> bool:
        """Delete user."""
        pass
    
    @abstractmethod
    async def exists_username(self, username: str) -> bool:
        """Check if username exists."""
        pass
    
    @abstractmethod
    async def exists_email(self, email: str) -> bool:
        """Check if email exists."""
        pass