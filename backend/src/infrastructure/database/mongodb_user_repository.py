"""MongoDB implementation of user repository."""

from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...domain.entities.user import User, UserId, SubscriptionType, UserStatus
from ...domain.repositories.user_repository import UserRepository


class MongoDBUserRepository(UserRepository):
    """MongoDB implementation of user repository."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = self.db.users
    
    async def save(self, user: User) -> None:
        """Save user to MongoDB."""
        user_doc = {
            "id": user.id.value,
            "username": user.username,
            "email": user.email,
            "password_hash": user.password_hash,
            "full_name": user.full_name,
            "status": user.status.value,
            "is_admin": user.is_admin,
            "subscription_type": user.subscription_type.value,
            "subscription_expires": user.subscription_expires,
            "api_token": user.api_token,
            "telegram_sessions": user.telegram_sessions,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        
        await self.collection.update_one(
            {"id": user.id.value},
            {"$set": user_doc},
            upsert=True
        )
    
    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find user by ID."""
        doc = await self.collection.find_one({"id": user_id.value})
        return self._doc_to_user(doc) if doc else None
    
    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username."""
        doc = await self.collection.find_one({"username": username})
        return self._doc_to_user(doc) if doc else None
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        doc = await self.collection.find_one({"email": email})
        return self._doc_to_user(doc) if doc else None
    
    async def find_by_api_token(self, api_token: str) -> Optional[User]:
        """Find user by API token."""
        doc = await self.collection.find_one({"api_token": api_token})
        return self._doc_to_user(doc) if doc else None
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination."""
        cursor = self.collection.find({}).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_user(doc) for doc in docs]
    
    async def count_by_subscription_type(self, subscription_type: SubscriptionType) -> int:
        """Count users by subscription type."""
        return await self.collection.count_documents({"subscription_type": subscription_type.value})
    
    async def delete(self, user_id: UserId) -> bool:
        """Delete user."""
        result = await self.collection.delete_one({"id": user_id.value})
        return result.deleted_count > 0
    
    async def exists_username(self, username: str) -> bool:
        """Check if username exists."""
        count = await self.collection.count_documents({"username": username})
        return count > 0
    
    async def exists_email(self, email: str) -> bool:
        """Check if email exists."""
        count = await self.collection.count_documents({"email": email})
        return count > 0
    
    def _doc_to_user(self, doc: dict) -> User:
        """Convert MongoDB document to User entity."""
        return User(
            id=UserId(doc["id"]),
            username=doc["username"],
            email=doc["email"],
            password_hash=doc["password_hash"],
            full_name=doc["full_name"],
            status=UserStatus(doc.get("status", "active")),
            is_admin=doc.get("is_admin", False),
            subscription_type=SubscriptionType(doc.get("subscription_type", "free")),
            subscription_expires=doc.get("subscription_expires"),
            api_token=doc.get("api_token"),
            telegram_sessions=doc.get("telegram_sessions", []),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at")
        )