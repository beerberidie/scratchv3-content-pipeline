"""
Base data models for the Scratch Automation App
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AIProvider(str, Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    LMSTUDIO = "lmstudio"


class ContentType(str, Enum):
    """Types of content that can be generated"""
    BLOG = "blog"
    ARTICLE = "article"
    NEWS = "news"
    SOCIAL_POST = "social_post"
    RESHARE = "reshare"


class BaseTimestampModel(BaseModel):
    """Base model with timestamp fields"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()


class User(BaseTimestampModel):
    """User model"""
    username: str
    email: str
    password_hash: str
    is_active: bool = True
    settings: Optional[Dict[str, Any]] = None


class UserSettings(BaseModel):
    """User settings model"""
    ai_provider: AIProvider = AIProvider.LMSTUDIO
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "google/gemini-2.0-flash-exp:free"
    pexels_api_key: Optional[str] = None
    wordpress_url_presets: List[str] = []
    wordpress_app_username: Optional[str] = None
    wordpress_app_password: Optional[str] = None


class ChatFile(BaseTimestampModel):
    """Chat file model"""
    filename: str
    content: str
    user_id: str
    file_size: int


class Task(BaseTimestampModel):
    """Task model for content generation"""
    id: str
    user_id: str
    topic: str
    rules: str
    article_content: Optional[str] = None
    include_image: bool = False
    scheduled_time: datetime
    process_enabled: bool = True
    wordpress_url: str
    referenced_chats: List[str] = []
    status: TaskStatus = TaskStatus.PENDING
    content_type: ContentType = ContentType.BLOG
    generated_content: Optional[str] = None
    image_urls: List[str] = []
    error_message: Optional[str] = None
    warning_message: Optional[str] = None
    wordpress_error: Optional[str] = None
    execution_log: List[Dict[str, Any]] = []


class GeneratedContent(BaseTimestampModel):
    """Generated content model"""
    id: str
    task_id: str
    user_id: str
    content: str
    content_type: ContentType
    image_urls: List[str] = []
    metadata: Dict[str, Any] = {}
    wordpress_posted: bool = False
    wordpress_posted_at: Optional[datetime] = None
    wordpress_post_id: Optional[str] = None
    wordpress_edit_link: Optional[str] = None
