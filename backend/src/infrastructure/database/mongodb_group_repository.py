"""MongoDB implementation of group repository."""

from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...domain.entities.group import Group, GroupId, GroupStatus, BlacklistReason
from ...domain.repositories.group_repository import GroupRepository


class MongoDBGroupRepository(GroupRepository):
    """MongoDB implementation of group repository."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = self.db.groups
    
    async def save(self, group: Group) -> None:
        """Save group to MongoDB."""
        group_doc = {
            "id": group.id.value,
            "telegram_id": group.telegram_id,
            "name": group.name,
            "username": group.username,
            "invite_link": group.invite_link,
            "status": group.status.value,
            "blacklist_reason": group.blacklist_reason.value if group.blacklist_reason else None,
            "blacklist_until": group.blacklist_until,
            "message_count": group.message_count,
            "last_message_sent": group.last_message_sent,
            "created_at": group.created_at,
            "updated_at": group.updated_at
        }
        
        await self.collection.update_one(
            {"id": group.id.value},
            {"$set": group_doc},
            upsert=True
        )
    
    async def find_by_id(self, group_id: GroupId) -> Optional[Group]:
        """Find group by ID."""
        doc = await self.collection.find_one({"id": group_id.value})
        return self._doc_to_group(doc) if doc else None
    
    async def find_by_telegram_id(self, telegram_id: str) -> Optional[Group]:
        """Find group by Telegram ID."""
        doc = await self.collection.find_one({"telegram_id": telegram_id})
        return self._doc_to_group(doc) if doc else None
    
    async def list_by_status(self, status: GroupStatus) -> List[Group]:
        """List groups by status."""
        cursor = self.collection.find({"status": status.value})
        docs = await cursor.to_list(length=None)
        return [self._doc_to_group(doc) for doc in docs]
    
    async def list_available_for_sending(self) -> List[Group]:
        """List groups available for sending messages."""
        # Groups that are active or have expired temporary blacklists
        cursor = self.collection.find({
            "$or": [
                {"status": GroupStatus.ACTIVE.value},
                {
                    "status": GroupStatus.BLACKLISTED_TEMP.value,
                    "blacklist_until": {"$lt": datetime.utcnow()}
                }
            ]
        })
        docs = await cursor.to_list(length=None)
        groups = []
        for doc in docs:
            group = self._doc_to_group(doc)
            if group.is_available_for_sending():
                groups.append(group)
        return groups
    
    async def count_by_status(self, status: GroupStatus) -> int:
        """Count groups by status."""
        return await self.collection.count_documents({"status": status.value})
    
    async def delete(self, group_id: GroupId) -> bool:
        """Delete group."""
        result = await self.collection.delete_one({"id": group_id.value})
        return result.deleted_count > 0
    
    async def bulk_save(self, groups: List[Group]) -> None:
        """Save multiple groups."""
        if not groups:
            return
        
        operations = []
        for group in groups:
            group_doc = {
                "id": group.id.value,
                "telegram_id": group.telegram_id,
                "name": group.name,
                "username": group.username,
                "invite_link": group.invite_link,
                "status": group.status.value,
                "blacklist_reason": group.blacklist_reason.value if group.blacklist_reason else None,
                "blacklist_until": group.blacklist_until,
                "message_count": group.message_count,
                "last_message_sent": group.last_message_sent,
                "created_at": group.created_at,
                "updated_at": group.updated_at
            }
            
            operations.append({
                "updateOne": {
                    "filter": {"id": group.id.value},
                    "update": {"$set": group_doc},
                    "upsert": True
                }
            })
        
        if operations:
            await self.collection.bulk_write(operations)
    
    def _doc_to_group(self, doc: dict) -> Group:
        """Convert MongoDB document to Group entity."""
        from datetime import datetime
        
        blacklist_reason = None
        if doc.get("blacklist_reason"):
            blacklist_reason = BlacklistReason(doc["blacklist_reason"])
        
        return Group(
            id=GroupId(doc["id"]),
            telegram_id=doc["telegram_id"],
            name=doc["name"],
            username=doc.get("username"),
            invite_link=doc.get("invite_link"),
            status=GroupStatus(doc.get("status", "active")),
            blacklist_reason=blacklist_reason,
            blacklist_until=doc.get("blacklist_until"),
            message_count=doc.get("message_count", 0),
            last_message_sent=doc.get("last_message_sent"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at")
        )