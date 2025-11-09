"""
Configuration settings for the Scratch Automation App
"""
import os
import logging
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    openrouter_api_key: Optional[str] = Field(None, env="OPENROUTER_API_KEY")
    pexels_api_key: Optional[str] = Field(None, env="PEXELS_API_KEY")
    
    # SMTP Configuration
    smtp_host: str = Field("smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(None, env="SMTP_PASSWORD")
    from_email: Optional[str] = Field(None, env="FROM_EMAIL")
    
    # Application Configuration
    secret_key: str = Field("change-me-in-production", env="SECRET_KEY")
    debug: bool = Field(False, env="DEBUG")
    environment: str = Field("production", env="ENVIRONMENT")
    
    # Redis Configuration
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    
    # File Storage
    upload_dir: str = Field("./uploads", env="UPLOAD_DIR")
    data_dir: str = Field("./data", env="DATA_DIR")
    
    # Rate Limiting
    max_requests_per_hour: int = Field(200, env="MAX_REQUESTS_PER_HOUR")
    max_requests_per_day: int = Field(2000, env="MAX_REQUESTS_PER_DAY")
    
    # Default AI Settings
    default_ai_provider: str = Field("lmstudio", env="DEFAULT_AI_PROVIDER")
    default_openai_model: str = Field("gpt-4", env="DEFAULT_OPENAI_MODEL")
    default_openrouter_model: str = Field("google/gemini-2.0-flash-exp:free", env="DEFAULT_OPENROUTER_MODEL")
    default_lmstudio_model: str = Field("qwen3-4b", env="DEFAULT_LMSTUDIO_MODEL")
    lmstudio_api_url: str = Field("http://localhost:1234/v1", env="LMSTUDIO_API_URL")
    
    # Server Configuration
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")

    # SSL Configuration
    ssl_keyfile: Optional[str] = Field(None, env="SSL_KEYFILE")
    ssl_certfile: Optional[str] = Field(None, env="SSL_CERTFILE")
    use_ssl: bool = Field(False, env="USE_SSL")

    # Security Configuration
    encryption_key: Optional[str] = Field(None, env="ENCRYPTION_KEY")
    enable_security_headers: bool = Field(True, env="ENABLE_SECURITY_HEADERS")
    force_https: bool = Field(False, env="FORCE_HTTPS")

    # File Upload Security
    max_upload_size: int = Field(10485760, env="MAX_UPLOAD_SIZE")  # 10MB
    allowed_extensions: str = Field("txt,md,json", env="ALLOWED_EXTENSIONS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure required directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.data_dir, exist_ok=True)
os.makedirs(f"{settings.data_dir}/users", exist_ok=True)
os.makedirs(f"{settings.data_dir}/tasks", exist_ok=True)
os.makedirs(f"{settings.data_dir}/history", exist_ok=True)
os.makedirs(f"{settings.data_dir}/chats", exist_ok=True)

# Configure logging to reduce noise from invalid HTTP requests
def configure_logging():
    """Configure logging to reduce noise from invalid requests"""
    # Reduce uvicorn access log level for invalid requests
    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.setLevel(logging.WARNING)

    # Create a custom filter to suppress "Invalid HTTP request received" warnings
    class InvalidRequestFilter(logging.Filter):
        def filter(self, record):
            return "Invalid HTTP request received" not in record.getMessage()

    # Apply filter to uvicorn error logger
    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.addFilter(InvalidRequestFilter())

# Apply logging configuration
configure_logging()
