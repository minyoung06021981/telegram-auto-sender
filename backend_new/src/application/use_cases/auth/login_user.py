"""Login user use case."""

from typing import Dict, Any
from dataclasses import dataclass

from ....domain.repositories.user_repository import UserRepository
from ....domain.services.authentication_service import AuthenticationService, AuthenticationError


@dataclass
class LoginUserCommand:
    """Command to login user."""
    username: str
    password: str


class LoginUserUseCase:
    """Use case for user login."""
    
    def __init__(self, user_repository: UserRepository, auth_service: AuthenticationService):
        self.user_repository = user_repository
        self.auth_service = auth_service
    
    async def execute(self, command: LoginUserCommand) -> Dict[str, Any]:
        """Execute login user use case."""
        # Validate input
        self._validate_command(command)
        
        try:
            # Authenticate user
            user = await self.auth_service.authenticate_user(command.username, command.password)
            
            # Create access token
            access_token = self.auth_service.create_access_token(user)
            
            return {
                "user": {
                    "id": user.id.value,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "subscription_type": user.subscription_type.value,
                    "subscription_active": user.is_subscription_active(),
                    "api_token": user.api_token,
                    "is_admin": user.is_admin
                },
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except AuthenticationError as e:
            raise ValueError(str(e))
    
    def _validate_command(self, command: LoginUserCommand) -> None:
        """Validate login command."""
        if not command.username or len(command.username.strip()) == 0:
            raise ValueError("Username is required")
        
        if not command.password or len(command.password.strip()) == 0:
            raise ValueError("Password is required")