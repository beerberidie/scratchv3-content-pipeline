"""
Authentication service with static user list and JWT tokens
"""
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.config import settings
from app.models.base import User, UserSettings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    """Authentication service for managing users and tokens"""
    
    def __init__(self):
        self.users_file = os.path.join(settings.data_dir, "users.json")
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Ensure users file exists with default users"""
        if not os.path.exists(self.users_file):
            # Create default users
            default_users = {
                "admin": {
                    "username": "admin",
                    "email": "admin@scratch.local",
                    "password_hash": self.get_password_hash("admin123"),
                    "is_active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "settings": {
                        "ai_provider": "lmstudio",
                        "openai_model": "gpt-4",
                        "openrouter_model": "google/gemini-2.0-flash-exp:free",
                        "email_presets": ["editor@example.com", "team@example.com"]
                    }
                },
                "demo": {
                    "username": "demo",
                    "email": "demo@scratch.local",
                    "password_hash": self.get_password_hash("demo123"),
                    "is_active": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "settings": {
                        "ai_provider": "openai",
                        "openai_model": "gpt-3.5-turbo",
                        "openrouter_model": "google/gemini-2.0-flash-exp:free",
                        "email_presets": ["test@example.com"]
                    }
                }
            }
            
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(default_users, f, indent=2)
    
    def _load_users(self) -> Dict[str, Any]:
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_users(self, users: Dict[str, Any]):
        """Save users to JSON file"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        users = self._load_users()
        return users.get(username)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password"""
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user["password_hash"]):
            return None
        if not user.get("is_active", True):
            return None
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return payload
        except JWTError:
            return None
    
    def get_current_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get current user from JWT token"""
        payload = self.verify_token(token)
        if payload is None:
            return None
        
        username = payload.get("sub")
        if username is None:
            return None
        
        user = self.get_user(username)
        if user is None:
            return None
        
        return user
    
    def create_user(self, username: str, email: str, password: str, settings: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new user"""
        users = self._load_users()
        if username in users:
            return False  # User already exists

        # Create new user
        users[username] = {
            "username": username,
            "email": email,
            "password_hash": self.get_password_hash(password),
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "settings": settings or {
                "ai_provider": "openrouter",
                "openai_model": "gpt-4",
                "openrouter_model": "google/gemini-2.0-flash-exp:free",
                "wordpress_url_presets": []
            }
        }

        self._save_users(users)
        return True

    def delete_user(self, username: str) -> bool:
        """Delete a user (for testing purposes)"""
        users = self._load_users()
        if username not in users:
            return False

        del users[username]
        self._save_users(users)
        return True

    def update_user_settings(self, username: str, settings_data: Dict[str, Any]) -> bool:
        """Update user settings"""
        users = self._load_users()
        if username not in users:
            return False

        users[username]["settings"] = settings_data
        users[username]["updated_at"] = datetime.utcnow().isoformat()
        self._save_users(users)
        return True


# Global auth service instance
auth_service = AuthService()
