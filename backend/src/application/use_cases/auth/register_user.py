"""Register user use case."""

import uuid
from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass

from ....domain.entities.user import User, UserId, UserStatus, SubscriptionType
from ....domain.repositories.user_repository import UserRepository
from ....domain.services.authentication_service import AuthenticationService


@dataclass
class RegisterUserCommand:
    """Command to register new user."""
    username: str
    email: str
    password: str
    full_name: str


class RegisterUserUseCase:
    """Use case for registering new user."""
    
    def __init__(self, user_repository: UserRepository, auth_service: AuthenticationService):
        self.user_repository = user_repository
        self.auth_service = auth_service
    
    async def execute(self, command: RegisterUserCommand) -> Dict[str, Any]:
        """Execute register user use case."""
        # Validate input
        await self._validate_command(command)
        
        # Check if user already exists
        if await self.user_repository.exists_username(command.username):
            raise ValueError("Username already exists")
        
        if await self.user_repository.exists_email(command.email):
            raise ValueError("Email already exists")
        
        # Create new user
        user = User(
            id=UserId(str(uuid.uuid4())),
            username=command.username,
            email=command.email,
            password_hash=self.auth_service.hash_password(command.password),
            full_name=command.full_name,
            status=UserStatus.ACTIVE,
            subscription_type=SubscriptionType.FREE,
            api_token=self.auth_service.generate_api_token(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save user
        await self.user_repository.save(user)
        
        # Create access token
        access_token = self.auth_service.create_access_token(user)
        
        return {
            "user": {
                "id": user.id.value,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "subscription_type": user.subscription_type.value,
                "api_token": user.api_token
            },
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    async def _validate_command(self, command: RegisterUserCommand) -> None:
        """Validate register command."""
        if not command.username or len(command.username.strip()) == 0:
            raise ValueError("Username is required")
        
        if len(command.username) < 3:
            raise ValueError("Username must be at least 3 characters")
        
        if not command.email or len(command.email.strip()) == 0:
            raise ValueError("Email is required")
        
        if "@" not in command.email:
            raise ValueError("Invalid email format")
        
        if not command.password or len(command.password) < 6:
            raise ValueError("Password must be at least 6 characters")
        
        if not command.full_name or len(command.full_name.strip()) == 0:
            raise ValueError("Full name is required")