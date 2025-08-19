"""Group domain entity."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class GroupStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED_TEMP = "blacklisted_temp"
    BLACKLISTED_PERM = "blacklisted_perm"


class BlacklistReason(Enum):
    FLOOD_WAIT = "flood_wait"
    SLOW_MODE = "slow_mode"
    USER_BANNED = "user_banned"
    CHAT_WRITE_FORBIDDEN = "chat_write_forbidden"
    CHANNEL_PRIVATE = "channel_private"
    PEER_ID_INVALID = "peer_id_invalid"


@dataclass(frozen=True)
class GroupId:
    """Value object for Group ID."""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Group ID cannot be empty")


@dataclass
class Group:
    """Group domain entity with blacklist logic."""
    
    id: GroupId
    telegram_id: str
    name: str
    username: Optional[str] = None
    invite_link: Optional[str] = None
    status: GroupStatus = GroupStatus.ACTIVE
    blacklist_reason: Optional[BlacklistReason] = None
    blacklist_until: Optional[datetime] = None
    message_count: int = 0
    last_message_sent: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def is_available_for_sending(self) -> bool:
        """Check if group is available for sending messages."""
        if self.status == GroupStatus.BLACKLISTED_PERM:
            return False
        
        if self.status == GroupStatus.BLACKLISTED_TEMP:
            if self.blacklist_until and self.blacklist_until > datetime.utcnow():
                return False
            else:
                # Temporary blacklist expired, reactivate
                self.activate()
        
        return self.status == GroupStatus.ACTIVE
    
    def blacklist_temporarily(self, reason: BlacklistReason, duration_seconds: int) -> None:
        """Temporarily blacklist group."""
        self.status = GroupStatus.BLACKLISTED_TEMP
        self.blacklist_reason = reason
        self.blacklist_until = datetime.utcnow() + datetime.timedelta(seconds=duration_seconds)
        self.updated_at = datetime.utcnow()
    
    def blacklist_permanently(self, reason: BlacklistReason) -> None:
        """Permanently blacklist group."""
        self.status = GroupStatus.BLACKLISTED_PERM
        self.blacklist_reason = reason
        self.blacklist_until = None
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate group and clear blacklist."""
        self.status = GroupStatus.ACTIVE
        self.blacklist_reason = None
        self.blacklist_until = None
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate group."""
        self.status = GroupStatus.INACTIVE
        self.updated_at = datetime.utcnow()
    
    def record_message_sent(self) -> None:
        """Record that a message was sent to this group."""
        self.message_count += 1
        self.last_message_sent = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_info(self, name: str, username: Optional[str] = None) -> None:
        """Update group information."""
        self.name = name
        if username is not None:
            self.username = username
        self.updated_at = datetime.utcnow()