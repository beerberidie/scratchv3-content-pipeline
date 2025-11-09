"""
Settings management API endpoints
"""
import os
import json
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.dependencies import get_current_active_user
from app.services.auth import auth_service
from app.services.ai import ai_service
from app.config import settings

router = APIRouter()


class UserSettingsRequest(BaseModel):
    ai_provider: str = "lmstudio"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "google/gemini-2.0-flash-exp:free"
    lmstudio_api_url: Optional[str] = None
    lmstudio_model: str = "qwen3-4b"
    pexels_api_key: Optional[str] = None
    wordpress_url_presets: List[str] = []
    wordpress_app_username: Optional[str] = None
    wordpress_app_password: Optional[str] = None


class UserSettingsResponse(BaseModel):
    ai_provider: str
    openai_model: str
    openrouter_model: str
    lmstudio_api_url: str
    lmstudio_model: str
    wordpress_url_presets: List[str]
    has_openai_key: bool
    has_openrouter_key: bool
    has_pexels_key: bool
    has_wordpress_credentials: bool


class ChatFileResponse(BaseModel):
    filename: str
    size: int
    uploaded_at: str


@router.get("/", response_model=UserSettingsResponse)
async def get_settings(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get user settings
    """
    user_settings = current_user.get("settings", {})

    return UserSettingsResponse(
        ai_provider=user_settings.get("ai_provider", "lmstudio"),
        openai_model=user_settings.get("openai_model", "gpt-4"),
        openrouter_model=user_settings.get("openrouter_model", "google/gemini-2.0-flash-exp:free"),
        lmstudio_api_url=user_settings.get("lmstudio_api_url", "http://localhost:1234/v1"),
        lmstudio_model=user_settings.get("lmstudio_model", "qwen3-4b"),
        wordpress_url_presets=user_settings.get("wordpress_url_presets", []),
        has_openai_key=bool(user_settings.get("openai_api_key")),
        has_openrouter_key=bool(user_settings.get("openrouter_api_key")),
        has_pexels_key=bool(user_settings.get("pexels_api_key")),
        has_wordpress_credentials=bool(user_settings.get("wordpress_app_username") and user_settings.get("wordpress_app_password"))
    )


@router.put("/", response_model=UserSettingsResponse)
async def update_settings(
    request: UserSettingsRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update user settings
    """
    # Prepare settings data
    settings_data = {
        "ai_provider": request.ai_provider,
        "openai_model": request.openai_model,
        "openrouter_model": request.openrouter_model,
        "lmstudio_model": request.lmstudio_model,
        "wordpress_url_presets": request.wordpress_url_presets
    }

    # Only store API keys and credentials if provided (don't overwrite with None)
    if request.openai_api_key:
        settings_data["openai_api_key"] = request.openai_api_key
    if request.openrouter_api_key:
        settings_data["openrouter_api_key"] = request.openrouter_api_key
    if request.lmstudio_api_url:
        settings_data["lmstudio_api_url"] = request.lmstudio_api_url
    if request.pexels_api_key:
        settings_data["pexels_api_key"] = request.pexels_api_key
    if request.wordpress_app_username:
        settings_data["wordpress_app_username"] = request.wordpress_app_username
    if request.wordpress_app_password:
        settings_data["wordpress_app_password"] = request.wordpress_app_password

    # Merge with existing settings to preserve API keys
    existing_settings = current_user.get("settings", {})
    existing_settings.update(settings_data)

    # Update user settings
    success = auth_service.update_user_settings(current_user["username"], existing_settings)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update settings")

    return UserSettingsResponse(
        ai_provider=settings_data["ai_provider"],
        openai_model=settings_data["openai_model"],
        openrouter_model=settings_data["openrouter_model"],
        lmstudio_api_url=existing_settings.get("lmstudio_api_url", "http://localhost:1234/v1"),
        lmstudio_model=settings_data["lmstudio_model"],
        wordpress_url_presets=settings_data["wordpress_url_presets"],
        has_openai_key=bool(existing_settings.get("openai_api_key")),
        has_openrouter_key=bool(existing_settings.get("openrouter_api_key")),
        has_pexels_key=bool(existing_settings.get("pexels_api_key")),
        has_wordpress_credentials=bool(existing_settings.get("wordpress_app_username") and existing_settings.get("wordpress_app_password"))
    )


@router.post("/upload-chat")
async def upload_chat_file(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Upload a chat file
    """
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")

    # Create user chat directory
    user_chat_dir = os.path.join(settings.data_dir, "chats", current_user["username"])
    os.makedirs(user_chat_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(user_chat_dir, file.filename)
    content = await file.read()

    with open(file_path, 'wb') as f:
        f.write(content)

    # Save metadata
    metadata = {
        "filename": file.filename,
        "size": len(content),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "content_type": file.content_type
    }

    metadata_file = os.path.join(user_chat_dir, f"{file.filename}.meta")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    return {
        "filename": file.filename,
        "size": len(content),
        "message": "File uploaded successfully"
    }


@router.get("/chats", response_model=List[ChatFileResponse])
async def get_chat_files(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get list of uploaded chat files
    """
    user_chat_dir = os.path.join(settings.data_dir, "chats", current_user["username"])

    if not os.path.exists(user_chat_dir):
        return []

    files = []
    for filename in os.listdir(user_chat_dir):
        if filename.endswith('.txt'):
            file_path = os.path.join(user_chat_dir, filename)
            metadata_file = os.path.join(user_chat_dir, f"{filename}.meta")

            # Get file stats
            stat = os.stat(file_path)
            uploaded_at = datetime.fromtimestamp(stat.st_mtime).isoformat()

            # Try to get metadata
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        uploaded_at = metadata.get("uploaded_at", uploaded_at)
                except:
                    pass

            files.append(ChatFileResponse(
                filename=filename,
                size=stat.st_size,
                uploaded_at=uploaded_at
            ))

    return sorted(files, key=lambda x: x.uploaded_at, reverse=True)


@router.get("/chats/{filename}")
async def get_chat_file(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Download a chat file
    """
    user_chat_dir = os.path.join(settings.data_dir, "chats", current_user["username"])
    file_path = os.path.join(user_chat_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Return file for download
    return FileResponse(
        file_path,
        filename=filename,
        media_type='text/plain'
    )


@router.delete("/chats/{filename}")
async def delete_chat_file(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Delete a chat file
    """
    user_chat_dir = os.path.join(settings.data_dir, "chats", current_user["username"])
    file_path = os.path.join(user_chat_dir, filename)
    metadata_file = os.path.join(user_chat_dir, f"{filename}.meta")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Delete file and metadata
    os.remove(file_path)
    if os.path.exists(metadata_file):
        os.remove(metadata_file)

    return {"message": f"File {filename} deleted successfully"}


@router.get("/lmstudio-models")
async def get_lmstudio_models(
    api_url: str = "http://localhost:1234/v1",
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get available models from LM Studio
    """
    result = await ai_service.get_lmstudio_models(api_url)
    return result
