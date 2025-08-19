"""Group repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.group import Group, GroupId, GroupStatus


class GroupRepository(ABC):
    """Abstract group repository interface."""
    
    @abstractmethod
    async def save(self, group: Group) -> None:
        """Save group to database."""
        pass
    
    @abstractmethod
    async def find_by_id(self, group_id: GroupId) -> Optional[Group]:
        """Find group by ID."""
        pass
    
    @abstractmethod
    async def find_by_telegram_id(self, telegram_id: str) -> Optional[Group]:
        """Find group by Telegram ID."""
        pass
    
    @abstractmethod
    async def list_by_status(self, status: GroupStatus) -> List[Group]:
        """List groups by status."""
        pass
    
    @abstractmethod
    async def list_available_for_sending(self) -> List[Group]:
        """List groups available for sending messages."""
        pass
    
    @abstractmethod
    async def count_by_status(self, status: GroupStatus) -> int:
        """Count groups by status."""
        pass
    
    @abstractmethod
    async def delete(self, group_id: GroupId) -> bool:
        """Delete group."""
        pass
    
    @abstractmethod
    async def bulk_save(self, groups: List[Group]) -> None:
        """Save multiple groups."""
        pass