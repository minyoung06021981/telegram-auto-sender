"""MongoDB implementation of telegram session repository."""

from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...domain.entities.telegram_session import (
    TelegramSession, SessionId, TelegramCredentials, TelegramUser, SessionStatus
)
from ...domain.repositories.telegram_session_repository import TelegramSessionRepository


class MongoDBTelegramSessionRepository(TelegramSessionRepository):
    """MongoDB implementation of telegram session repository."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = self.db.telegram_sessions
    
    async def save(self, session: TelegramSession) -> None:
        """Save session to MongoDB."""
        session_doc = {
            "id": session.id.value,
            "user_id": session.user_id,
            "phone_number": session.phone_number,
            "api_id": session.credentials.api_id,
            "api_hash": session.credentials.api_hash,
            "encrypted_session_data": session.encrypted_session_data,
            "telegram_user": {
                "id": session.telegram_user.id,
                "first_name": session.telegram_user.first_name,
                "last_name": session.telegram_user.last_name,
                "username": session.telegram_user.username,
                "phone": session.telegram_user.phone
            } if session.telegram_user else None,
            "status": session.status.value,
            "last_used_at": session.last_used_at,
            "created_at": session.created_at,
            "updated_at": session.updated_at
        }
        
        await self.collection.update_one(
            {"id": session.id.value},
            {"$set": session_doc},
            upsert=True
        )
    
    async def find_by_id(self, session_id: SessionId) -> Optional[TelegramSession]:
        """Find session by ID."""
        doc = await self.collection.find_one({"id": session_id.value})
        return self._doc_to_session(doc) if doc else None
    
    async def find_by_user_id(self, user_id: str) -> List[TelegramSession]:
        """Find sessions by user ID."""
        cursor = self.collection.find({"user_id": user_id})
        docs = await cursor.to_list(length=None)
        return [self._doc_to_session(doc) for doc in docs]
    
    async def find_by_phone_number(self, phone_number: str) -> Optional[TelegramSession]:
        """Find session by phone number."""
        doc = await self.collection.find_one({"phone_number": phone_number})
        return self._doc_to_session(doc) if doc else None
    
    async def list_active_sessions(self) -> List[TelegramSession]:
        """List all active sessions."""
        cursor = self.collection.find({"status": "active"})
        docs = await cursor.to_list(length=None)
        return [self._doc_to_session(doc) for doc in docs]
    
    async def delete(self, session_id: SessionId) -> bool:
        """Delete session."""
        result = await self.collection.delete_one({"id": session_id.value})
        return result.deleted_count > 0
    
    async def count_by_user(self, user_id: str) -> int:
        """Count sessions by user."""
        return await self.collection.count_documents({"user_id": user_id})
    
    def _doc_to_session(self, doc: dict) -> TelegramSession:
        """Convert MongoDB document to TelegramSession entity."""
        telegram_user = None
        if doc.get("telegram_user"):
            tu = doc["telegram_user"]
            telegram_user = TelegramUser(
                id=tu["id"],
                first_name=tu["first_name"],
                last_name=tu.get("last_name"),
                username=tu.get("username"),
                phone=tu.get("phone")
            )
        
        return TelegramSession(
            id=SessionId(doc["id"]),
            user_id=doc["user_id"],
            phone_number=doc["phone_number"],
            credentials=TelegramCredentials(
                api_id=doc["api_id"],
                api_hash=doc["api_hash"]
            ),
            encrypted_session_data=doc["encrypted_session_data"],
            telegram_user=telegram_user,
            status=SessionStatus(doc.get("status", "active")),
            last_used_at=doc.get("last_used_at"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at")
        )