"""Authentication domain service."""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from ..entities.user import User, UserId, UserStatus
from ..repositories.user_repository import UserRepository


class AuthenticationError(Exception):
    """Authentication related errors."""
    pass


class AuthenticationService:
    """Domain service for user authentication."""
    
    def __init__(self, user_repository: UserRepository, jwt_secret: str, jwt_algorithm: str = "HS256"):
        self.user_repository = user_repository
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt."""
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        return f"{salt}${pwd_hash}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        try:
            salt, stored_hash = password_hash.split('$')
            pwd_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
            return pwd_hash == stored_hash
        except ValueError:
            return False
    
    def create_access_token(self, user: User, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        if expires_delta is None:
            expires_delta = timedelta(days=7)
        
        payload = {
            "user_id": user.id.value,
            "username": user.username,
            "exp": datetime.utcnow() + expires_delta,
            "iat": datetime.utcnow(),
            "is_admin": user.is_admin
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
    
    async def authenticate_user(self, username: str, password: str) -> User:
        """Authenticate user with username and password."""
        user = await self.user_repository.find_by_username(username)
        
        if not user:
            raise AuthenticationError("Invalid username or password")
        
        if not self.verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid username or password")
        
        if user.status != UserStatus.ACTIVE:
            raise AuthenticationError("Account is disabled")
        
        return user
    
    async def authenticate_by_token(self, token: str) -> User:
        """Authenticate user by JWT token."""
        payload = self.verify_token(token)
        
        user = await self.user_repository.find_by_id(UserId(payload["user_id"]))
        
        if not user:
            raise AuthenticationError("User not found")
        
        if user.status != UserStatus.ACTIVE:
            raise AuthenticationError("Account is disabled")
        
        return user
    
    async def authenticate_by_api_token(self, api_token: str) -> User:
        """Authenticate user by API token."""
        user = await self.user_repository.find_by_api_token(api_token)
        
        if not user:
            raise AuthenticationError("Invalid API token")
        
        if user.status != UserStatus.ACTIVE:
            raise AuthenticationError("Account is disabled")
        
        return user
    
    def generate_api_token(self) -> str:
        """Generate new API token."""
        return f"tk_{secrets.token_urlsafe(32)}"