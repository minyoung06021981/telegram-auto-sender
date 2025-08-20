"""Authentication API routes."""

import os
import httpx
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from ....application.use_cases.auth.register_user import RegisterUserUseCase, RegisterUserCommand
from ....application.use_cases.auth.login_user import LoginUserUseCase, LoginUserCommand
from ....domain.entities.user import User
from ....domain.repositories.user_repository import UserRepository
from ....domain.services.authentication_service import AuthenticationService
from ..dependencies import get_user_repository, get_authentication_service, get_current_active_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


# Request/Response Models
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    subscription_type: str
    subscription_active: bool
    api_token: str | None = None
    is_admin: bool


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: RegisterRequest,
    user_repository: UserRepository = Depends(get_user_repository),
    auth_service: AuthenticationService = Depends(get_authentication_service)
):
    """Register a new user."""
    use_case = RegisterUserUseCase(user_repository, auth_service)
    command = RegisterUserCommand(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name
    )
    
    try:
        result = await use_case.execute(command)
        return TokenResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login_user(
    request: LoginRequest,
    user_repository: UserRepository = Depends(get_user_repository),
    auth_service: AuthenticationService = Depends(get_authentication_service)
):
    """Login user with username and password."""
    use_case = LoginUserUseCase(user_repository, auth_service)
    command = LoginUserCommand(
        username=request.username,
        password=request.password
    )
    
    try:
        result = await use_case.execute(command)
        return TokenResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information."""
    return UserResponse(
        id=current_user.id.value,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        subscription_type=current_user.subscription_type.value,
        subscription_active=current_user.is_subscription_active(),
        api_token=current_user.api_token,
        is_admin=current_user.is_admin
    )


@router.post("/refresh-api-token")
async def refresh_api_token(
    current_user: User = Depends(get_current_active_user),
    user_repository: UserRepository = Depends(get_user_repository),
    auth_service: AuthenticationService = Depends(get_authentication_service)
):
    """Refresh user's API token."""
    # Generate new API token
    new_token = auth_service.generate_api_token()
    current_user.api_token = new_token
    current_user.updated_at = current_user.updated_at  # This will be set in the entity
    
    # Save updated user
    await user_repository.save(current_user)
    
    return {"api_token": new_token}