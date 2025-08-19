"""Telegram API routes."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from ....application.use_cases.telegram.create_session import CreateSessionUseCase, CreateSessionCommand
from ....application.use_cases.telegram.authenticate_session import AuthenticateSessionUseCase, AuthenticateSessionCommand
from ....domain.entities.user import User
from ....domain.entities.telegram_session import SessionId
from ....domain.repositories.telegram_session_repository import TelegramSessionRepository
from ....domain.services.telegram_service import TelegramService
from ..dependencies import get_current_active_user, get_telegram_session_repository, get_telegram_service


router = APIRouter(prefix="/telegram", tags=["Telegram"])


# Request/Response Models
class CreateSessionRequest(BaseModel):
    api_id: int
    api_hash: str
    phone_number: str


class AuthenticateSessionRequest(BaseModel):
    session_id: str
    phone_code: Optional[str] = None
    password: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: str
    phone_number: str
    is_authenticated: bool
    telegram_user: dict | None = None
    requires_code: bool = False
    requires_password: bool = False


@router.post("/sessions", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_telegram_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_active_user),
    session_repository: TelegramSessionRepository = Depends(get_telegram_session_repository),
    telegram_service: TelegramService = Depends(get_telegram_service)
):
    """Create new Telegram session."""
    use_case = CreateSessionUseCase(session_repository, telegram_service)
    command = CreateSessionCommand(
        user_id=current_user.id.value,
        api_id=request.api_id,
        api_hash=request.api_hash,
        phone_number=request.phone_number
    )
    
    try:
        result = await use_case.execute(command)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/sessions/authenticate", response_model=dict)
async def authenticate_telegram_session(
    request: AuthenticateSessionRequest,
    current_user: User = Depends(get_current_active_user),
    session_repository: TelegramSessionRepository = Depends(get_telegram_session_repository),
    telegram_service: TelegramService = Depends(get_telegram_service)
):
    """Authenticate Telegram session with code or password."""
    use_case = AuthenticateSessionUseCase(session_repository, telegram_service)
    command = AuthenticateSessionCommand(
        session_id=request.session_id,
        phone_code=request.phone_code,
        password=request.password
    )
    
    try:
        result = await use_case.execute(command)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/sessions", response_model=list[SessionResponse])
async def get_user_sessions(
    current_user: User = Depends(get_current_active_user),
    session_repository: TelegramSessionRepository = Depends(get_telegram_session_repository),
    telegram_service: TelegramService = Depends(get_telegram_service)
):
    """Get all user's Telegram sessions."""
    sessions = await session_repository.find_by_user_id(current_user.id.value)
    
    session_responses = []
    for session in sessions:
        session_info = await telegram_service.get_session_info(session.id)
        if session_info:
            session_responses.append(SessionResponse(
                session_id=session_info["session_id"],
                phone_number=session_info["phone_number"],
                is_authenticated=session_info["is_authenticated"],
                telegram_user=session_info["telegram_user"]
            ))
    
    return session_responses


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session_info(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    telegram_service: TelegramService = Depends(get_telegram_service)
):
    """Get specific session information."""
    session_info = await telegram_service.get_session_info(SessionId(session_id))
    
    if not session_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    return SessionResponse(
        session_id=session_info["session_id"],
        phone_number=session_info["phone_number"],
        is_authenticated=session_info["is_authenticated"],
        telegram_user=session_info["telegram_user"]
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    session_repository: TelegramSessionRepository = Depends(get_telegram_session_repository)
):
    """Delete Telegram session."""
    session = await session_repository.find_by_id(SessionId(session_id))
    
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    # Verify session belongs to current user
    if session.user_id != current_user.id.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    success = await session_repository.delete(SessionId(session_id))
    
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete session")


@router.post("/sessions/{session_id}/load", response_model=dict)
async def load_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    session_repository: TelegramSessionRepository = Depends(get_telegram_session_repository)
):
    """Load existing Telegram session."""
    session = await session_repository.find_by_id(SessionId(session_id))
    
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    # Verify session belongs to current user
    if session.user_id != current_user.id.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if not session.is_valid():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")
    
    # Mark session as used
    session.mark_as_used()
    await session_repository.save(session)
    
    return {
        "session_id": session_id,
        "authenticated": True,
        "telegram_user": {
            "id": session.telegram_user.id,
            "first_name": session.telegram_user.first_name,
            "last_name": session.telegram_user.last_name,
            "username": session.telegram_user.username
        } if session.telegram_user else None
    }