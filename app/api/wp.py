"""
WordPress Settings Management API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from app.dependencies import get_current_active_user
from app.services.storage import storage_service
from app.api.keys import encrypt_key, decrypt_key

router = APIRouter()


class WordPressSite(BaseModel):
    url: HttpUrl


class WordPressSiteResponse(BaseModel):
    id: str
    url: str
    created_at: str


class WordPressAuth(BaseModel):
    username: str
    password: str


class WordPressAuthStatus(BaseModel):
    configured: bool
    username: Optional[str] = None


@router.get("/sites", response_model=List[WordPressSiteResponse])
async def get_wordpress_sites(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get all WordPress sites for the current user
    """
    user_id = current_user["email"]
    
    try:
        sites = storage_service.get_wp_sites(user_id)
        return sites
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve WordPress sites: {str(e)}"
        )


@router.post("/sites", response_model=WordPressSiteResponse)
async def add_wordpress_site(
    site: WordPressSite,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Add a new WordPress site URL
    """
    user_id = current_user["email"]
    url = str(site.url)
    
    # Check if URL already exists
    existing_sites = storage_service.get_wp_sites(user_id)
    if any(existing_site["url"] == url for existing_site in existing_sites):
        raise HTTPException(
            status_code=400,
            detail="WordPress site URL already exists"
        )
    
    try:
        # Generate unique ID and create site record
        site_id = str(uuid.uuid4())
        site_data = {
            "id": site_id,
            "url": url,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Add to storage
        storage_service.add_wp_site(user_id, site_data)
        
        return WordPressSiteResponse(**site_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add WordPress site: {str(e)}"
        )


@router.delete("/sites/{site_id}")
async def delete_wordpress_site(
    site_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Delete a WordPress site by ID
    """
    user_id = current_user["email"]
    
    try:
        # Check if site exists
        sites = storage_service.get_wp_sites(user_id)
        site_exists = any(site["id"] == site_id for site in sites)
        
        if not site_exists:
            raise HTTPException(
                status_code=404,
                detail="WordPress site not found"
            )
        
        # Remove from storage
        storage_service.delete_wp_site(user_id, site_id)
        
        return {"success": True, "message": "WordPress site deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete WordPress site: {str(e)}"
        )


@router.get("/auth", response_model=WordPressAuthStatus)
async def get_wordpress_auth_status(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get WordPress authentication status
    """
    user_id = current_user["email"]

    try:
        # First check new encrypted storage system
        auth_data = storage_service.get_wp_auth(user_id)

        if auth_data and auth_data.get("username_encrypted") and auth_data.get("password_encrypted"):
            # Decrypt username for display
            username = decrypt_key(auth_data["username_encrypted"])
            return WordPressAuthStatus(configured=True, username=username)

        # If no credentials found in new system, check legacy system (users.json)
        user_settings = current_user.get("settings", {})
        legacy_username = user_settings.get("wordpress_app_username")
        legacy_password = user_settings.get("wordpress_app_password")

        if legacy_username and legacy_password:
            return WordPressAuthStatus(configured=True, username=legacy_username)
        else:
            return WordPressAuthStatus(configured=False)

    except Exception as e:
        return WordPressAuthStatus(configured=False)


@router.post("/auth")
async def save_wordpress_auth(
    auth: WordPressAuth,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Save WordPress authentication credentials
    """
    user_id = current_user["email"]
    
    # Validate credentials
    if not auth.username or not auth.password:
        raise HTTPException(
            status_code=400,
            detail="Both username and password are required"
        )
    
    if len(auth.username.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Username must be at least 2 characters long"
        )
    
    if len(auth.password.strip()) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters long"
        )
    
    try:
        # Encrypt credentials
        username_encrypted = encrypt_key(auth.username.strip())
        password_encrypted = encrypt_key(auth.password.strip())
        
        # Save to storage
        auth_data = {
            "username_encrypted": username_encrypted,
            "password_encrypted": password_encrypted,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        storage_service.save_wp_auth(user_id, auth_data)
        
        return {
            "success": True,
            "message": "WordPress credentials saved successfully",
            "status": WordPressAuthStatus(configured=True, username=auth.username.strip())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save WordPress credentials: {str(e)}"
        )


@router.delete("/auth")
async def delete_wordpress_auth(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Delete WordPress authentication credentials
    """
    user_id = current_user["email"]
    
    try:
        storage_service.delete_wp_auth(user_id)
        
        return {
            "success": True,
            "message": "WordPress credentials deleted successfully",
            "status": WordPressAuthStatus(configured=False)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete WordPress credentials: {str(e)}"
        )


def get_decrypted_wp_auth(user_id: str) -> Optional[Dict[str, str]]:
    """
    Internal function to get decrypted WordPress credentials for use by other services
    """
    try:
        # First check new encrypted storage system
        auth_data = storage_service.get_wp_auth(user_id)
        if auth_data and auth_data.get("username_encrypted") and auth_data.get("password_encrypted"):
            return {
                "username": decrypt_key(auth_data["username_encrypted"]),
                "password": decrypt_key(auth_data["password_encrypted"])
            }

        # If no credentials found in new system, check legacy system (users.json)
        # Note: This requires getting user data by email (user_id)
        from app.services.auth import auth_service
        users = auth_service._load_users()

        # Find user by email
        user_data = None
        for username, user_info in users.items():
            if user_info.get("email") == user_id:
                user_data = user_info
                break

        if user_data:
            user_settings = user_data.get("settings", {})
            legacy_username = user_settings.get("wordpress_app_username")
            legacy_password = user_settings.get("wordpress_app_password")

            if legacy_username and legacy_password:
                return {
                    "username": legacy_username,
                    "password": legacy_password
                }

        return None
    except Exception:
        return None
