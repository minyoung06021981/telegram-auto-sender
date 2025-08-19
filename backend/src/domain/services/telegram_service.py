"""Telegram integration domain service."""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from ..entities.telegram_session import TelegramSession, SessionId, TelegramCredentials, TelegramUser, SessionStatus
from ..entities.group import Group, GroupStatus, BlacklistReason
from ..repositories.telegram_session_repository import TelegramSessionRepository


class TelegramError(Exception):
    """Telegram related errors."""
    pass


class TelegramFloodError(TelegramError):
    """Flood wait error."""
    def __init__(self, seconds: int):
        self.seconds = seconds
        super().__init__(f"Flood wait: {seconds} seconds")


class TelegramService:
    """Domain service for Telegram operations."""
    
    def __init__(self, session_repository: TelegramSessionRepository):
        self.session_repository = session_repository
        self.active_clients = {}  # In-memory client cache
    
    async def validate_credentials(self, credentials: TelegramCredentials) -> bool:
        """Validate Telegram API credentials."""
        try:
            # This would integrate with actual Telegram client validation
            # For now, just check basic format
            return credentials.api_id > 0 and len(credentials.api_hash) > 0
        except Exception:
            return False
    
    async def create_session(self, user_id: str, phone_number: str, credentials: TelegramCredentials) -> SessionId:
        """Create new Telegram session."""
        session_id = SessionId(f"session_{phone_number}_{datetime.utcnow().timestamp()}")
        
        # Check for existing session with same phone
        existing = await self.session_repository.find_by_phone_number(phone_number)
        if existing:
            raise TelegramError("Session already exists for this phone number")
        
        session = TelegramSession(
            id=session_id,
            user_id=user_id,
            phone_number=phone_number,
            credentials=credentials,
            encrypted_session_data="",  # Will be populated after auth
            status=SessionStatus.ACTIVE
        )
        
        await self.session_repository.save(session)
        return session_id
    
    async def authenticate_session(self, session_id: SessionId, phone_code: Optional[str] = None, 
                                 password: Optional[str] = None) -> Dict[str, Any]:
        """Authenticate Telegram session with code/password."""
        session = await self.session_repository.find_by_id(session_id)
        if not session:
            raise TelegramError("Session not found")
        
        # This would integrate with actual Telegram client authentication
        # For now, simulate the process
        
        if phone_code:
            # Validate phone code
            if len(phone_code) < 5:
                raise TelegramError("Invalid phone code")
            
            # Check if 2FA is required (simulate)
            requires_password = phone_code == "12345"  # Mock condition
            
            if requires_password:
                return {
                    "authenticated": False,
                    "requires_password": True
                }
        
        if password:
            # Validate 2FA password
            if len(password) < 1:
                raise TelegramError("Invalid password")
        
        # Mock successful authentication
        telegram_user = TelegramUser(
            id=12345,
            first_name="Test",
            last_name="User",
            username="testuser",
            phone=session.phone_number
        )
        
        session.update_telegram_user(telegram_user)
        session.mark_as_used()
        
        await self.session_repository.save(session)
        
        return {
            "authenticated": True,
            "user_info": {
                "id": telegram_user.id,
                "first_name": telegram_user.first_name,
                "last_name": telegram_user.last_name,
                "username": telegram_user.username
            }
        }
    
    async def validate_group_identifier(self, session_id: SessionId, identifier: str) -> Dict[str, Any]:
        """Validate if group exists and user has access."""
        session = await self.session_repository.find_by_id(session_id)
        if not session or not session.is_valid():
            raise TelegramError("Invalid or expired session")
        
        try:
            # This would integrate with actual Telegram client
            # For now, simulate validation
            
            # Parse different identifier formats
            if identifier.startswith('@'):
                # Username format
                group_id = f"-100{hash(identifier) % 1000000000}"
                title = identifier[1:].title() + " Group"
            elif identifier.startswith('https://t.me/'):
                # Invite link format
                group_id = f"-100{hash(identifier) % 1000000000}"
                title = "Invite Link Group"
            elif identifier.startswith('-'):
                # Direct ID format
                group_id = identifier
                title = f"Group {identifier}"
            else:
                raise TelegramError("Invalid group identifier format")
            
            return {
                "valid": True,
                "id": group_id,
                "title": title,
                "username": identifier[1:] if identifier.startswith('@') else None
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def send_message_to_group(self, session_id: SessionId, group: Group, message: str) -> Dict[str, Any]:
        """Send message to Telegram group."""
        session = await self.session_repository.find_by_id(session_id)
        if not session or not session.is_valid():
            raise TelegramError("Invalid or expired session")
        
        if not group.is_available_for_sending():
            raise TelegramError("Group is not available for sending")
        
        try:
            # This would integrate with actual Telegram client
            # For now, simulate message sending with potential errors
            
            # Simulate different error conditions
            import random
            error_chance = random.random()
            
            if error_chance < 0.05:  # 5% chance of flood error
                wait_seconds = random.randint(30, 300)
                group.blacklist_temporarily(BlacklistReason.FLOOD_WAIT, wait_seconds)
                raise TelegramFloodError(wait_seconds)
            elif error_chance < 0.08:  # 3% chance of slow mode
                group.blacklist_temporarily(BlacklistReason.SLOW_MODE, 60)
                raise TelegramError("Slow mode active")
            elif error_chance < 0.10:  # 2% chance of permanent ban
                group.blacklist_permanently(BlacklistReason.USER_BANNED)
                raise TelegramError("User banned in channel")
            
            # Simulate successful send
            await asyncio.sleep(0.1)  # Simulate network delay
            group.record_message_sent()
            session.mark_as_used()
            
            return {
                "success": True,
                "message_id": random.randint(1000, 9999)
            }
            
        except TelegramFloodError:
            raise
        except Exception as e:
            raise TelegramError(f"Failed to send message: {str(e)}")
    
    async def get_session_info(self, session_id: SessionId) -> Optional[Dict[str, Any]]:
        """Get session information."""
        session = await self.session_repository.find_by_id(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.id.value,
            "phone_number": session.phone_number,
            "is_authenticated": session.status == SessionStatus.ACTIVE,
            "telegram_user": {
                "id": session.telegram_user.id,
                "first_name": session.telegram_user.first_name,
                "last_name": session.telegram_user.last_name,
                "username": session.telegram_user.username
            } if session.telegram_user else None,
            "last_used_at": session.last_used_at,
            "created_at": session.created_at
        }