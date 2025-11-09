"""
Authentication API endpoints
"""
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.services.auth import auth_service, ACCESS_TOKEN_EXPIRE_MINUTES
from app.dependencies import get_current_active_user

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str
    email: str
    expires_in: int


class UserResponse(BaseModel):
    username: str
    email: str
    is_active: bool
    created_at: str
    settings: Optional[Dict[str, Any]] = None


@router.get("/login")
async def login_info():
    """
    Get login endpoint information
    """
    return {
        "message": "Login endpoint - use POST method",
        "method": "POST",
        "required_fields": ["username", "password"],
        "optional_fields": ["remember_me"],
        "example": {
            "username": "demo",
            "password": "demo123",
            "remember_me": False
        }
    }


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user with username and password
    """
    user = auth_service.authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES * (7 if request.remember_me else 1)
    )
    access_token = auth_service.create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user["username"],
        username=user["username"],
        email=user["email"],
        expires_in=int(access_token_expires.total_seconds())
    )


@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Logout user (client should discard token)
    """
    return {"message": f"Successfully logged out user: {current_user['username']}"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get current authenticated user information
    """
    return UserResponse(
        username=current_user["username"],
        email=current_user["email"],
        is_active=current_user.get("is_active", True),
        created_at=current_user.get("created_at", ""),
        settings=current_user.get("settings")
    )


@router.get("/users")
async def list_users(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    List all available users (for admin purposes)
    """
    # Only show usernames for security
    users = auth_service._load_users()
    return {
        "users": [
            {
                "username": username,
                "email": user_data.get("email", ""),
                "is_active": user_data.get("is_active", True)
            }
            for username, user_data in users.items()
        ]
    }
