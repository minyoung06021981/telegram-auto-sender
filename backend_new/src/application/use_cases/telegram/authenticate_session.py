"""Authenticate Telegram session use case."""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from ....domain.entities.telegram_session import SessionId, TelegramCredentials
from ....domain.repositories.telegram_session_repository import TelegramSessionRepository
from ....domain.services.telegram_service import TelegramService, TelegramError


@dataclass
class AuthenticateSessionCommand:
    """Command to authenticate Telegram session."""
    session_id: str
    phone_code: Optional[str] = None
    password: Optional[str] = None


class AuthenticateSessionUseCase:
    """Use case for Telegram session authentication."""
    
    def __init__(self, session_repository: TelegramSessionRepository, telegram_service: TelegramService):
        self.session_repository = session_repository
        self.telegram_service = telegram_service
    
    async def execute(self, command: AuthenticateSessionCommand) -> Dict[str, Any]:
        """Execute authenticate session use case."""
        try:
            session_id = SessionId(command.session_id)
            
            result = await self.telegram_service.authenticate_session(
                session_id=session_id,
                phone_code=command.phone_code,
                password=command.password
            )
            
            return {
                "session_id": command.session_id,
                **result
            }
            
        except TelegramError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Authentication failed: {str(e)}")