"""Message template domain entity."""

from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateId:
    """Value object for Template ID."""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Template ID cannot be empty")


@dataclass
class MessageTemplate:
    """Message template domain entity."""
    
    id: TemplateId
    name: str
    content: str
    is_default: bool = False
    variables: Dict[str, Any] = None
    usage_count: int = 0
    last_used_at: datetime = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def validate_content(self) -> bool:
        """Validate template content."""
        if not self.content or len(self.content.strip()) == 0:
            return False
        
        if len(self.content) > 4096:  # Telegram message limit
            return False
        
        return True
    
    def validate_name(self) -> bool:
        """Validate template name."""
        if not self.name or len(self.name.strip()) == 0:
            return False
        
        if len(self.name) > 100:
            return False
        
        return True
    
    def render_content(self, variables: Dict[str, Any] = None) -> str:
        """Render template content with variables."""
        content = self.content
        
        # Merge template variables with provided variables
        all_variables = {**self.variables}
        if variables:
            all_variables.update(variables)
        
        # Simple variable substitution
        for key, value in all_variables.items():
            placeholder = f"{{{key}}}"
            content = content.replace(placeholder, str(value))
        
        return content
    
    def set_as_default(self) -> None:
        """Mark this template as default."""
        self.is_default = True
        self.updated_at = datetime.utcnow()
    
    def unset_as_default(self) -> None:
        """Unmark this template as default."""
        self.is_default = False
        self.updated_at = datetime.utcnow()
    
    def record_usage(self) -> None:
        """Record template usage."""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_content(self, name: str, content: str, variables: Dict[str, Any] = None) -> None:
        """Update template content."""
        self.name = name
        self.content = content
        if variables is not None:
            self.variables = variables
        self.updated_at = datetime.utcnow()