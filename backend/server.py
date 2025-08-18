from fastapi import FastAPI, APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, FloodWaitError, SlowModeWaitError
from telethon.errors.rpcerrorlist import UserBannedInChannelError, ChatWriteForbiddenError, ChannelPrivateError, PeerIdInvalidError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cryptography.fernet import Fernet
import socketio
import os
import logging
import asyncio
import json
import uuid
import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
import redis.asyncio as redis

# Setup
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
mongo_client = AsyncIOMotorClient(mongo_url)
db = mongo_client[os.environ['DB_NAME']]

# Redis connection for blacklist management
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True, db=0)

# Encryption key for session storage
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key().decode())
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

# FastAPI app
app = FastAPI(title="Telegram Auto Sender", version="1.0.0")
api_router = APIRouter(prefix="/api")

# Socket.IO for real-time updates
sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socket_app = socketio.ASGIApp(sio, app)

# Scheduler for message sending
scheduler = AsyncIOScheduler()
scheduler.start()

# Security
security = HTTPBearer()

# Global variables for active sessions
active_sessions = {}
message_jobs = {}

# Pydantic Models
class TelegramAuth(BaseModel):
    api_id: int
    api_hash: str
    phone_number: str

class TelegramVerify(BaseModel):
    phone_code: Optional[str] = None
    password: Optional[str] = None
    session_id: str
    phone_number: Optional[str] = None

class GroupCreate(BaseModel):
    name: str
    username: Optional[str] = None
    group_id: Optional[str] = None
    invite_link: Optional[str] = None

class Group(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    username: Optional[str] = None
    group_id: str
    invite_link: Optional[str] = None
    status: str = "active"  # active, inactive, blacklisted_temp, blacklisted_perm
    blacklist_reason: Optional[str] = None
    blacklist_until: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MessageTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    content: str
    is_default: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MessageTemplateCreate(BaseModel):
    name: str
    content: str
    is_default: bool = False

class AppSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    min_message_interval: int = 5  # seconds
    max_message_interval: int = 15  # seconds
    min_cycle_interval: int = 60  # minutes
    max_cycle_interval: int = 120  # minutes
    max_retry_attempts: int = 3
    is_scheduler_active: bool = False
    theme: str = "auto"  # auto, light, dark
    notifications_enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SessionInfo(BaseModel):
    session_id: str
    phone_number: str
    is_authenticated: bool
    user_info: Optional[Dict[str, Any]] = None

class SendMessageJob(BaseModel):
    group_ids: List[str]
    message_template_id: str
    send_immediately: bool = False

# Helper Functions
def encrypt_session(session_string: str) -> str:
    """Encrypt session string for secure storage"""
    return cipher_suite.encrypt(session_string.encode()).decode()

def decrypt_session(encrypted_session: str) -> str:
    """Decrypt session string for usage"""
    return cipher_suite.decrypt(encrypted_session.encode()).decode()

async def get_active_client(session_id: str) -> Optional[TelegramClient]:
    """Get active Telegram client from session"""
    return active_sessions.get(session_id)

async def validate_telegram_group(client: TelegramClient, group_identifier: str) -> Dict[str, Any]:
    """Validate if group exists and user has access"""
    try:
        if group_identifier.startswith('@'):
            entity = await client.get_entity(group_identifier)
        elif group_identifier.startswith('https://t.me/'):
            entity = await client.get_entity(group_identifier)
        else:
            entity = await client.get_entity(int(group_identifier))
        
        return {
            "valid": True,
            "id": str(entity.id),
            "title": entity.title,
            "username": getattr(entity, 'username', None)
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }

async def send_message_to_group(client: TelegramClient, group_id: str, message: str, session_id: str) -> Dict[str, Any]:
    """Send message to a specific group with error handling"""
    try:
        await client.send_message(int(group_id), message)
        
        # Log success
        await db.message_logs.insert_one({
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "group_id": group_id,
            "message": message,
            "status": "success",
            "timestamp": datetime.utcnow()
        })
        
        return {"success": True, "message": "Message sent successfully"}
        
    except FloodWaitError as e:
        # Handle flood wait - temporary blacklist
        wait_time = e.seconds
        await redis_client.setex(f"blacklist:flood:{group_id}", wait_time, "flood_wait")
        
        # Update group status
        await db.groups.update_one(
            {"group_id": group_id},
            {
                "$set": {
                    "status": "blacklisted_temp",
                    "blacklist_reason": "flood_wait",
                    "blacklist_until": datetime.utcnow() + timedelta(seconds=wait_time),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        await log_error(session_id, group_id, message, "FloodWaitError", str(e))
        return {"success": False, "error": "flood_wait", "wait_seconds": wait_time}
        
    except SlowModeWaitError as e:
        # Handle slow mode - skip for this cycle
        await redis_client.sadd("blacklist:slowmode_cycle", group_id)
        
        await db.groups.update_one(
            {"group_id": group_id},
            {
                "$set": {
                    "status": "blacklisted_temp",
                    "blacklist_reason": "slow_mode",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        await log_error(session_id, group_id, message, "SlowModeWaitError", str(e))
        return {"success": False, "error": "slow_mode"}
        
    except (UserBannedInChannelError, ChatWriteForbiddenError, ChannelPrivateError, PeerIdInvalidError) as e:
        # Permanent blacklist errors
        await db.groups.update_one(
            {"group_id": group_id},
            {
                "$set": {
                    "status": "blacklisted_perm",
                    "blacklist_reason": e.__class__.__name__,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Remove from temporary blacklists if exists
        await redis_client.srem("blacklist:slowmode_cycle", group_id)
        await redis_client.delete(f"blacklist:flood:{group_id}")
        
        await log_error(session_id, group_id, message, e.__class__.__name__, str(e))
        return {"success": False, "error": "permanent_ban", "error_type": e.__class__.__name__}
        
    except Exception as e:
        await log_error(session_id, group_id, message, "UnknownError", str(e))
        return {"success": False, "error": "unknown", "message": str(e)}

async def log_error(session_id: str, group_id: str, message: str, error_type: str, error_message: str):
    """Log error to database"""
    await db.message_logs.insert_one({
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "group_id": group_id,
        "message": message,
        "status": "error",
        "error_type": error_type,
        "error_message": error_message,
        "timestamp": datetime.utcnow()
    })

async def cleanup_temporary_blacklists():
    """Cleanup temporary blacklists at the start of each cycle"""
    # Clear slow mode blacklist
    await redis_client.delete("blacklist:slowmode_cycle")
    
    # Update database for groups that are no longer in temporary blacklist
    await db.groups.update_many(
        {"status": "blacklisted_temp", "blacklist_reason": "slow_mode"},
        {
            "$set": {
                "status": "active",
                "blacklist_reason": None,
                "updated_at": datetime.utcnow()
            }
        }
    )

async def get_available_groups(session_id: str) -> List[str]:
    """Get list of groups that are available for sending (not blacklisted)"""
    # Get groups that are not permanently blacklisted
    active_groups = await db.groups.find({
        "status": {"$nin": ["blacklisted_perm"]}
    }).to_list(None)
    
    available_group_ids = []
    
    for group in active_groups:
        group_id = group["group_id"]
        
        # Check if group is in flood wait
        if await redis_client.exists(f"blacklist:flood:{group_id}"):
            continue
            
        # Check if group is in slow mode blacklist for current cycle
        if await redis_client.sismember("blacklist:slowmode_cycle", group_id):
            continue
            
        available_group_ids.append(group_id)
    
    return available_group_ids

# API Routes

@api_router.post("/auth/login")
async def telegram_login(auth_data: TelegramAuth):
    """Initialize Telegram login process"""
    try:
        session_id = str(uuid.uuid4())
        client = TelegramClient(
            StringSession(),
            auth_data.api_id,
            auth_data.api_hash,
            device_model="Telegram Auto Sender",
            system_version="1.0.0",
            app_version="1.0.0"
        )
        
        await client.connect()
        
        if not await client.is_user_authorized():
            sent_code = await client.send_code_request(auth_data.phone_number)
            
            # Store client in active sessions
            active_sessions[session_id] = client
            
            return {
                "session_id": session_id,
                "phone_code_hash": sent_code.phone_code_hash,
                "requires_code": True,
                "requires_password": False
            }
        else:
            me = await client.get_me()
            session_string = client.session.save()
            
            # Encrypt and store session
            encrypted_session = encrypt_session(session_string)
            await db.sessions.insert_one({
                "id": session_id,
                "phone_number": auth_data.phone_number,
                "api_id": auth_data.api_id,
                "api_hash": auth_data.api_hash,
                "encrypted_session": encrypted_session,
                "user_info": {
                    "id": me.id,
                    "first_name": me.first_name,
                    "last_name": me.last_name,
                    "username": me.username
                },
                "created_at": datetime.utcnow()
            })
            
            active_sessions[session_id] = client
            
            return {
                "session_id": session_id,
                "authenticated": True,
                "user_info": {
                    "id": me.id,
                    "first_name": me.first_name,
                    "last_name": me.last_name,
                    "username": me.username
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/auth/verify")
async def telegram_verify(verify_data: TelegramVerify):
    """Verify phone code or password"""
    try:
        client = active_sessions.get(verify_data.session_id)
        if not client:
            raise HTTPException(status_code=400, detail="Invalid session")
        
        # Handle phone code verification
        if verify_data.phone_code and not verify_data.password:
            try:
                await client.sign_in(code=verify_data.phone_code)
                # If we reach here, phone code was successful and no 2FA needed
            except SessionPasswordNeededError:
                # 2FA password is required
                return {
                    "session_id": verify_data.session_id,
                    "requires_password": True,
                    "authenticated": False
                }
        
        # Handle password verification (2FA)
        if verify_data.password:
            try:
                await client.sign_in(password=verify_data.password)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid 2FA password: {str(e)}")
        
        # Verify client is now authenticated
        if not await client.is_user_authorized():
            raise HTTPException(status_code=400, detail="Authentication failed")
            
        # Get user info and save session
        me = await client.get_me()
        session_string = client.session.save()
        
        # Encrypt and store session
        encrypted_session = encrypt_session(session_string)
        
        # Store session data with phone number
        phone_number = getattr(verify_data, 'phone_number', 'unknown')
        
        await db.sessions.update_one(
            {"id": verify_data.session_id},
            {
                "$set": {
                    "phone_number": phone_number,
                    "encrypted_session": encrypted_session,
                    "user_info": {
                        "id": me.id,
                        "first_name": me.first_name,
                        "last_name": me.last_name,
                        "username": me.username
                    },
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {
            "session_id": verify_data.session_id,
            "authenticated": True,
            "user_info": {
                "id": me.id,
                "first_name": me.first_name,
                "last_name": me.last_name,
                "username": me.username
            }
        }
        
    except PhoneCodeInvalidError:
        raise HTTPException(status_code=400, detail="Invalid phone code")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/auth/sessions")
async def get_sessions():
    """Get all saved sessions"""
    sessions = await db.sessions.find({}).to_list(None)
    return [
        SessionInfo(
            session_id=session["id"],
            phone_number=session.get("phone_number", ""),
            is_authenticated=True,
            user_info=session.get("user_info")
        ) for session in sessions
    ]

@api_router.post("/auth/load-session/{session_id}")
async def load_session(session_id: str):
    """Load existing session"""
    try:
        session_doc = await db.sessions.find_one({"id": session_id})
        if not session_doc:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Decrypt session string
        decrypted_session = decrypt_session(session_doc["encrypted_session"])
        
        # Create client with stored session
        client = TelegramClient(
            StringSession(decrypted_session),
            session_doc.get("api_id"),
            session_doc.get("api_hash"),
            device_model="Telegram Auto Sender",
            system_version="1.0.0",
            app_version="1.0.0"
        )
        
        await client.connect()
        
        if await client.is_user_authorized():
            active_sessions[session_id] = client
            return {
                "session_id": session_id,
                "authenticated": True,
                "user_info": session_doc.get("user_info")
            }
        else:
            raise HTTPException(status_code=401, detail="Session expired")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.delete("/auth/session/{session_id}")
async def delete_session(session_id: str):
    """Delete session"""
    # Remove from active sessions
    if session_id in active_sessions:
        client = active_sessions[session_id]
        await client.disconnect()
        del active_sessions[session_id]
    
    # Remove from database
    await db.sessions.delete_one({"id": session_id})
    
    return {"message": "Session deleted successfully"}

# Group Management Routes

@api_router.post("/groups", response_model=Group)
async def create_group(group_data: GroupCreate, session_id: str):
    """Add new group"""
    client = await get_active_client(session_id)
    if not client:
        raise HTTPException(status_code=401, detail="No active session")
    
    # Determine group identifier
    identifier = group_data.username or group_data.invite_link or group_data.group_id
    if not identifier:
        raise HTTPException(status_code=400, detail="Group identifier required")
    
    # Validate group
    validation = await validate_telegram_group(client, identifier)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=f"Invalid group: {validation['error']}")
    
    # Check if group already exists
    existing = await db.groups.find_one({"group_id": validation["id"]})
    if existing:
        raise HTTPException(status_code=400, detail="Group already exists")
    
    # Create group
    group = Group(
        name=group_data.name or validation["title"],
        username=validation.get("username"),
        group_id=validation["id"],
        invite_link=group_data.invite_link
    )
    
    await db.groups.insert_one(group.dict())
    return group

@api_router.get("/groups", response_model=List[Group])
async def get_groups():
    """Get all groups"""
    groups = await db.groups.find({}).to_list(None)
    return [Group(**group) for group in groups]

@api_router.get("/groups/stats")
async def get_group_stats():
    """Get group statistics"""
    total_groups = await db.groups.count_documents({})
    active_groups = await db.groups.count_documents({"status": "active"})
    temp_blacklisted = await db.groups.count_documents({"status": "blacklisted_temp"})
    perm_blacklisted = await db.groups.count_documents({"status": "blacklisted_perm"})
    
    return {
        "total": total_groups,
        "active": active_groups,
        "temp_blacklisted": temp_blacklisted,
        "perm_blacklisted": perm_blacklisted
    }

@api_router.delete("/groups/{group_id}")
async def delete_group(group_id: str):
    """Delete group"""
    result = await db.groups.delete_one({"id": group_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"message": "Group deleted successfully"}

# Message Template Routes

@api_router.post("/templates", response_model=MessageTemplate)
async def create_template(template_data: MessageTemplateCreate):
    """Create message template"""
    # If setting as default, unset other defaults
    if template_data.is_default:
        await db.message_templates.update_many(
            {},
            {"$set": {"is_default": False}}
        )
    
    template = MessageTemplate(**template_data.dict())
    await db.message_templates.insert_one(template.dict())
    return template

@api_router.get("/templates", response_model=List[MessageTemplate])
async def get_templates():
    """Get all message templates"""
    templates = await db.message_templates.find({}).to_list(None)
    return [MessageTemplate(**template) for template in templates]

@api_router.get("/templates/default", response_model=MessageTemplate)
async def get_default_template():
    """Get default message template"""
    template = await db.message_templates.find_one({"is_default": True})
    if not template:
        raise HTTPException(status_code=404, detail="No default template found")
    return MessageTemplate(**template)

@api_router.put("/templates/{template_id}")
async def update_template(template_id: str, template_data: MessageTemplateCreate):
    """Update message template"""
    # If setting as default, unset other defaults
    if template_data.is_default:
        await db.message_templates.update_many(
            {},
            {"$set": {"is_default": False}}
        )
    
    update_data = template_data.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.message_templates.update_one(
        {"id": template_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"message": "Template updated successfully"}

@api_router.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    """Delete message template"""
    result = await db.message_templates.delete_one({"id": template_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted successfully"}

# Message Sending Routes

@api_router.post("/messages/send")
async def send_messages(job_data: SendMessageJob, session_id: str, background_tasks: BackgroundTasks):
    """Send messages to groups"""
    client = await get_active_client(session_id)
    if not client:
        raise HTTPException(status_code=401, detail="No active session")
    
    # Get message template
    template = await db.message_templates.find_one({"id": job_data.message_template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Message template not found")
    
    if job_data.send_immediately:
        # Send immediately in background
        background_tasks.add_task(
            send_messages_job, 
            session_id, 
            job_data.group_ids, 
            template["content"]
        )
        return {"message": "Messages queued for immediate sending"}
    else:
        # Schedule for later (add to scheduler)
        job_id = str(uuid.uuid4())
        message_jobs[job_id] = {
            "session_id": session_id,
            "group_ids": job_data.group_ids,
            "message": template["content"],
            "status": "scheduled"
        }
        return {"message": "Messages scheduled", "job_id": job_id}

async def send_messages_job(session_id: str, group_ids: List[str], message: str):
    """Background job to send messages"""
    client = await get_active_client(session_id)
    if not client:
        return
    
    # Get app settings for delays
    settings = await db.settings.find_one({}) or AppSettings().dict()
    
    results = []
    
    for group_id in group_ids:
        # Check if group is available (not blacklisted)
        available_groups = await get_available_groups(session_id)
        if group_id not in available_groups:
            results.append({
                "group_id": group_id,
                "success": False,
                "error": "Group is blacklisted"
            })
            continue
        
        # Send message with retry logic
        max_retries = settings.get("max_retry_attempts", 3)
        for attempt in range(max_retries):
            result = await send_message_to_group(client, group_id, message, session_id)
            
            if result["success"]:
                results.append({
                    "group_id": group_id,
                    "success": True
                })
                break
            elif result.get("error") in ["flood_wait", "slow_mode", "permanent_ban"]:
                # Don't retry for these errors
                results.append({
                    "group_id": group_id,
                    "success": False,
                    "error": result["error"]
                })
                break
            elif attempt < max_retries - 1:
                # Retry with exponential backoff for other errors
                wait_time = (2 ** attempt) * 5
                await asyncio.sleep(wait_time)
            else:
                # Final attempt failed
                results.append({
                    "group_id": group_id,
                    "success": False,
                    "error": result.get("error", "unknown")
                })
        
        # Random delay between messages
        if group_id != group_ids[-1]:  # Not the last group
            delay = random.randint(
                settings.get("min_message_interval", 5),
                settings.get("max_message_interval", 15)
            )
            await asyncio.sleep(delay)
    
    # Emit results via Socket.IO
    await sio.emit('message_results', {
        'session_id': session_id,
        'results': results,
        'timestamp': datetime.utcnow().isoformat()
    })

# Settings Routes

@api_router.get("/settings", response_model=AppSettings)
async def get_settings():
    """Get application settings"""
    settings = await db.settings.find_one({})
    if not settings:
        # Create default settings
        settings = AppSettings()
        await db.settings.insert_one(settings.dict())
    return AppSettings(**settings)

@api_router.put("/settings")
async def update_settings(settings_data: AppSettings):
    """Update application settings"""
    await db.settings.update_one(
        {},
        {"$set": settings_data.dict()},
        upsert=True
    )
    return {"message": "Settings updated successfully"}

# Scheduler Routes

@api_router.post("/scheduler/start")
async def start_scheduler(session_id: str):
    """Start automatic message scheduler"""
    settings = await db.settings.find_one({}) or AppSettings().dict()
    
    # Clear existing jobs for this session
    for job in scheduler.get_jobs():
        if job.id.startswith(f"auto_sender_{session_id}"):
            job.remove()
    
    # Schedule recurring job
    min_interval = settings.get("min_cycle_interval", 60)
    max_interval = settings.get("max_cycle_interval", 120)
    next_run = datetime.now() + timedelta(minutes=random.randint(min_interval, max_interval))
    
    scheduler.add_job(
        auto_sender_cycle,
        "date",
        run_date=next_run,
        args=[session_id],
        id=f"auto_sender_{session_id}"
    )
    
    # Update settings
    await db.settings.update_one(
        {},
        {"$set": {"is_scheduler_active": True}},
        upsert=True
    )
    
    return {"message": "Scheduler started", "next_run": next_run.isoformat()}

@api_router.post("/scheduler/stop")
async def stop_scheduler(session_id: str):
    """Stop automatic message scheduler"""
    # Remove all jobs for this session
    for job in scheduler.get_jobs():
        if job.id.startswith(f"auto_sender_{session_id}"):
            job.remove()
    
    # Update settings
    await db.settings.update_one(
        {},
        {"$set": {"is_scheduler_active": False}},
        upsert=True
    )
    
    return {"message": "Scheduler stopped"}

async def auto_sender_cycle(session_id: str):
    """Automatic sender cycle job"""
    try:
        # Cleanup temporary blacklists
        await cleanup_temporary_blacklists()
        
        # Get default message template
        template = await db.message_templates.find_one({"is_default": True})
        if not template:
            return
        
        # Get available groups
        available_groups = await get_available_groups(session_id)
        if not available_groups:
            return
        
        # Send messages
        await send_messages_job(session_id, available_groups, template["content"])
        
        # Schedule next cycle
        settings = await db.settings.find_one({}) or AppSettings().dict()
        if settings.get("is_scheduler_active", False):
            min_interval = settings.get("min_cycle_interval", 60)
            max_interval = settings.get("max_cycle_interval", 120)
            next_run = datetime.now() + timedelta(minutes=random.randint(min_interval, max_interval))
            
            scheduler.add_job(
                auto_sender_cycle,
                "date",
                run_date=next_run,
                args=[session_id],
                id=f"auto_sender_{session_id}"
            )
    
    except Exception as e:
        logging.error(f"Error in auto sender cycle: {e}")

# Dashboard and Monitoring Routes

@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    # Get basic stats
    total_groups = await db.groups.count_documents({})
    active_groups = await db.groups.count_documents({"status": "active"})
    temp_blacklisted = await db.groups.count_documents({"status": "blacklisted_temp"})
    perm_blacklisted = await db.groups.count_documents({"status": "blacklisted_perm"})
    
    # Get message stats for last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    messages_sent = await db.message_logs.count_documents({
        "status": "success",
        "timestamp": {"$gte": yesterday}
    })
    messages_failed = await db.message_logs.count_documents({
        "status": "error",
        "timestamp": {"$gte": yesterday}
    })
    
    # Get scheduler status
    settings = await db.settings.find_one({}) or {}
    is_active = settings.get("is_scheduler_active", False)
    
    return {
        "groups": {
            "total": total_groups,
            "active": active_groups,
            "temp_blacklisted": temp_blacklisted,
            "perm_blacklisted": perm_blacklisted
        },
        "messages": {
            "sent_24h": messages_sent,
            "failed_24h": messages_failed
        },
        "scheduler": {
            "active": is_active
        }
    }

@api_router.get("/logs/messages")
async def get_message_logs(limit: int = 100, offset: int = 0):
    """Get message logs"""
    logs = await db.message_logs.find({}).sort("timestamp", -1).skip(offset).limit(limit).to_list(limit)
    return logs

# Socket.IO Events

@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    logging.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logging.info(f"Client disconnected: {sid}")

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # Disconnect all Telegram clients
    for client in active_sessions.values():
        await client.disconnect()
    
    # Close database connections
    mongo_client.close()
    await redis_client.close()
    
    # Stop scheduler
    scheduler.shutdown()

# Root route for health check
@app.get("/")
async def root():
    return {"message": "Telegram Auto Sender API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)