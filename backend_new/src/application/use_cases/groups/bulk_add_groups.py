"""Bulk add groups use case."""

import uuid
from typing import Dict, Any, List
from dataclasses import dataclass

from ....domain.entities.group import Group, GroupId
from ....domain.entities.telegram_session import SessionId
from ....domain.repositories.group_repository import GroupRepository
from ....domain.services.telegram_service import TelegramService, TelegramError


@dataclass
class BulkAddGroupsCommand:
    """Command to bulk add groups."""
    session_id: str
    identifiers: List[str]  # List of username/group_id/invite_link


class BulkAddGroupsUseCase:
    """Use case for adding multiple groups."""
    
    def __init__(self, group_repository: GroupRepository, telegram_service: TelegramService):
        self.group_repository = group_repository
        self.telegram_service = telegram_service
    
    async def execute(self, command: BulkAddGroupsCommand) -> Dict[str, Any]:
        """Execute bulk add groups use case."""
        try:
            # Validate input
            self._validate_command(command)
            
            session_id = SessionId(command.session_id)
            
            results = {
                "added": [],
                "skipped": [],
                "errors": []
            }
            
            groups_to_save = []
            
            for identifier in command.identifiers:
                identifier = identifier.strip()
                if not identifier:
                    continue
                
                try:
                    # Validate group through Telegram
                    validation_result = await self.telegram_service.validate_group_identifier(
                        session_id, identifier
                    )
                    
                    if not validation_result["valid"]:
                        results["errors"].append({
                            "identifier": identifier,
                            "error": validation_result["error"]
                        })
                        continue
                    
                    # Check if group already exists
                    existing = await self.group_repository.find_by_telegram_id(validation_result["id"])
                    if existing:
                        results["skipped"].append({
                            "identifier": identifier,
                            "name": validation_result["title"],
                            "reason": "Already exists"
                        })
                        continue
                    
                    # Create group entity
                    group = Group(
                        id=GroupId(str(uuid.uuid4())),
                        telegram_id=validation_result["id"],
                        name=validation_result["title"],
                        username=validation_result.get("username"),
                        invite_link=identifier if identifier.startswith('https://t.me/+') else None
                    )
                    
                    groups_to_save.append(group)
                    
                    results["added"].append({
                        "identifier": identifier,
                        "name": validation_result["title"],
                        "group_id": validation_result["id"]
                    })
                    
                except Exception as e:
                    results["errors"].append({
                        "identifier": identifier,
                        "error": str(e)
                    })
            
            # Bulk save groups
            if groups_to_save:
                await self.group_repository.bulk_save(groups_to_save)
            
            return results
            
        except TelegramError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Bulk add failed: {str(e)}")
    
    def _validate_command(self, command: BulkAddGroupsCommand) -> None:
        """Validate bulk add groups command."""
        if not command.session_id or len(command.session_id.strip()) == 0:
            raise ValueError("Session ID is required")
        
        if not command.identifiers or len(command.identifiers) == 0:
            raise ValueError("At least one group identifier is required")