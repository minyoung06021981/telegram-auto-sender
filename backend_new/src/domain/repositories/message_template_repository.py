"""Message template repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.message_template import MessageTemplate, TemplateId


class MessageTemplateRepository(ABC):
    """Abstract message template repository interface."""
    
    @abstractmethod
    async def save(self, template: MessageTemplate) -> None:
        """Save template to database."""
        pass
    
    @abstractmethod
    async def find_by_id(self, template_id: TemplateId) -> Optional[MessageTemplate]:
        """Find template by ID."""
        pass
    
    @abstractmethod
    async def find_default_template(self) -> Optional[MessageTemplate]:
        """Find default template."""
        pass
    
    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[MessageTemplate]:
        """Find template by name."""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[MessageTemplate]:
        """List all templates."""
        pass
    
    @abstractmethod
    async def delete(self, template_id: TemplateId) -> bool:
        """Delete template."""
        pass
    
    @abstractmethod
    async def clear_default_flags(self) -> None:
        """Clear all default flags."""
        pass
    
    @abstractmethod
    async def count_templates(self) -> int:
        """Count total templates."""
        pass