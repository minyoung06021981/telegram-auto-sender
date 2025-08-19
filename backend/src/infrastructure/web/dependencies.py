"""FastAPI dependencies for dependency injection."""

import os
from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.telegram_session_repository import TelegramSessionRepository
from ...domain.repositories.group_repository import GroupRepository
from ...domain.repositories.message_template_repository import MessageTemplateRepository
from ...domain.services.authentication_service import AuthenticationService
from ...domain.services.telegram_service import TelegramService
from ...infrastructure.database.mongodb_user_repository import MongoDBUserRepository
from ...infrastructure.database.mongodb_telegram_session_repository import MongoDBTelegramSessionRepository


# Security
security = HTTPBearer()

# Global database instance
_db_client = None
_database = None


@lru_cache()
def get_settings():
    """Get application settings."""
    return {
        "mongo_url": os.environ.get("MONGO_URL"),
        "db_name": os.environ.get("DB_NAME", "telegram_auto_sender"),
        "jwt_secret": os.environ.get("JWT_SECRET", "your-secret-key"),
        "jwt_algorithm": "HS256"
    }


async def get_database() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance."""
    global _db_client, _database
    
    if _database is None:
        settings = get_settings()
        _db_client = AsyncIOMotorClient(settings["mongo_url"])
        _database = _db_client[settings["db_name"]]
    
    return _database


async def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> UserRepository:
    """Get user repository instance."""
    return MongoDBUserRepository(db)


async def get_telegram_session_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> TelegramSessionRepository:
    """Get telegram session repository instance."""
    return MongoDBTelegramSessionRepository(db)


async def get_authentication_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> AuthenticationService:
    """Get authentication service instance."""
    settings = get_settings()
    return AuthenticationService(
        user_repository=user_repository,
        jwt_secret=settings["jwt_secret"],
        jwt_algorithm=settings["jwt_algorithm"]
    )


async def get_telegram_service(
    session_repository: TelegramSessionRepository = Depends(get_telegram_session_repository)
) -> TelegramService:
    """Get telegram service instance."""
    return TelegramService(session_repository)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = Depends(get_authentication_service)
) -> User:
    """Get current authenticated user."""
    try:
        token = credentials.credentials
        user = await auth_service.authenticate_by_token(token)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if current_user.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current admin user."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# Optional dependencies for public endpoints
async def get_optional_current_user(
    auth_service: AuthenticationService = Depends(get_authentication_service),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
) -> User | None:
    """Get current user if token is provided (optional)."""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = await auth_service.authenticate_by_token(token)
        return user
    except Exception:
        return None