"""Create Telegram session use case."""

from typing import Dict, Any
from dataclasses import dataclass

from ....domain.entities.telegram_session import TelegramCredentials
from ....domain.repositories.telegram_session_repository import TelegramSessionRepository
from ....domain.services.telegram_service import TelegramService, TelegramError


@dataclass
class CreateSessionCommand:
    """Command to create Telegram session."""
    user_id: str
    api_id: int
    api_hash: str
    phone_number: str


class CreateSessionUseCase:
    """Use case for creating Telegram session."""
    
    def __init__(self, session_repository: TelegramSessionRepository, telegram_service: TelegramService):
        self.session_repository = session_repository
        self.telegram_service = telegram_service
    
    async def execute(self, command: CreateSessionCommand) -> Dict[str, Any]:
        """Execute create session use case."""
        try:
            # Validate input
            self._validate_command(command)
            
            # Create credentials
            credentials = TelegramCredentials(
                api_id=command.api_id,
                api_hash=command.api_hash
            )
            
            # Validate credentials
            if not await self.telegram_service.validate_credentials(credentials):
                raise ValueError("Invalid Telegram credentials")
            
            # Create session
            session_id = await self.telegram_service.create_session(
                user_id=command.user_id,
                phone_number=command.phone_number,
                credentials=credentials
            )
            
            return {
                "session_id": session_id.value,
                "phone_number": command.phone_number,
                "requires_code": True,
                "requires_password": False
            }
            
        except TelegramError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Session creation failed: {str(e)}")
    
    def _validate_command(self, command: CreateSessionCommand) -> None:
        """Validate create session command."""
        if not command.user_id or len(command.user_id.strip()) == 0:
            raise ValueError("User ID is required")
        
        if not command.api_id or command.api_id <= 0:
            raise ValueError("Valid API ID is required")
        
        if not command.api_hash or len(command.api_hash.strip()) == 0:
            raise ValueError("API Hash is required")
        
        if not command.phone_number or len(command.phone_number.strip()) == 0:
            raise ValueError("Phone number is required")