"""MongoDB implementation of message template repository."""

from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...domain.entities.message_template import MessageTemplate, TemplateId
from ...domain.repositories.message_template_repository import MessageTemplateRepository


class MongoDBMessageTemplateRepository(MessageTemplateRepository):
    """MongoDB implementation of message template repository."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = self.db.message_templates
    
    async def save(self, template: MessageTemplate) -> None:
        """Save template to MongoDB."""
        template_doc = {
            "id": template.id.value,
            "name": template.name,
            "content": template.content,
            "is_default": template.is_default,
            "variables": template.variables,
            "usage_count": template.usage_count,
            "last_used_at": template.last_used_at,
            "created_at": template.created_at,
            "updated_at": template.updated_at
        }
        
        await self.collection.update_one(
            {"id": template.id.value},
            {"$set": template_doc},
            upsert=True
        )
    
    async def find_by_id(self, template_id: TemplateId) -> Optional[MessageTemplate]:
        """Find template by ID."""
        doc = await self.collection.find_one({"id": template_id.value})
        return self._doc_to_template(doc) if doc else None
    
    async def find_default_template(self) -> Optional[MessageTemplate]:
        """Find default template."""
        doc = await self.collection.find_one({"is_default": True})
        return self._doc_to_template(doc) if doc else None
    
    async def find_by_name(self, name: str) -> Optional[MessageTemplate]:
        """Find template by name."""
        doc = await self.collection.find_one({"name": name})
        return self._doc_to_template(doc) if doc else None
    
    async def list_all(self) -> List[MessageTemplate]:
        """List all templates."""
        cursor = self.collection.find({})
        docs = await cursor.to_list(length=None)
        return [self._doc_to_template(doc) for doc in docs]
    
    async def delete(self, template_id: TemplateId) -> bool:
        """Delete template."""
        result = await self.collection.delete_one({"id": template_id.value})
        return result.deleted_count > 0
    
    async def clear_default_flags(self) -> None:
        """Clear all default flags."""
        await self.collection.update_many(
            {"is_default": True},
            {"$set": {"is_default": False}}
        )
    
    async def count_templates(self) -> int:
        """Count total templates."""
        return await self.collection.count_documents({})
    
    def _doc_to_template(self, doc: dict) -> MessageTemplate:
        """Convert MongoDB document to MessageTemplate entity."""
        return MessageTemplate(
            id=TemplateId(doc["id"]),
            name=doc["name"],
            content=doc["content"],
            is_default=doc.get("is_default", False),
            variables=doc.get("variables", {}),
            usage_count=doc.get("usage_count", 0),
            last_used_at=doc.get("last_used_at"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at")
        )