"""Add group use case."""

import uuid
from typing import Dict, Any
from dataclasses import dataclass

from ....domain.entities.group import Group, GroupId
from ....domain.entities.telegram_session import SessionId
from ....domain.repositories.group_repository import GroupRepository
from ....domain.services.telegram_service import TelegramService, TelegramError


@dataclass
class AddGroupCommand:
    """Command to add group."""
    session_id: str
    identifier: str  # Can be username, group_id, or invite_link


class AddGroupUseCase:
    """Use case for adding single group."""
    
    def __init__(self, group_repository: GroupRepository, telegram_service: TelegramService):
        self.group_repository = group_repository
        self.telegram_service = telegram_service
    
    async def execute(self, command: AddGroupCommand) -> Dict[str, Any]:
        """Execute add group use case."""
        try:
            # Validate input
            self._validate_command(command)
            
            session_id = SessionId(command.session_id)
            
            # Validate group through Telegram
            validation_result = await self.telegram_service.validate_group_identifier(
                session_id, command.identifier
            )
            
            if not validation_result["valid"]:
                raise ValueError(f"Invalid group: {validation_result['error']}")
            
            # Check if group already exists
            existing = await self.group_repository.find_by_telegram_id(validation_result["id"])
            if existing:
                raise ValueError("Group already exists")
            
            # Create group entity
            group = Group(
                id=GroupId(str(uuid.uuid4())),
                telegram_id=validation_result["id"],
                name=validation_result["title"],
                username=validation_result.get("username"),
                invite_link=command.identifier if command.identifier.startswith('https://t.me/+') else None
            )
            
            # Save group
            await self.group_repository.save(group)
            
            return {
                "id": group.id.value,
                "telegram_id": group.telegram_id,
                "name": group.name,
                "username": group.username,
                "invite_link": group.invite_link,
                "status": group.status.value,
                "created_at": group.created_at.isoformat()
            }
            
        except TelegramError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Failed to add group: {str(e)}")
    
    def _validate_command(self, command: AddGroupCommand) -> None:
        """Validate add group command."""
        if not command.session_id or len(command.session_id.strip()) == 0:
            raise ValueError("Session ID is required")
        
        if not command.identifier or len(command.identifier.strip()) == 0:
            raise ValueError("Group identifier is required")