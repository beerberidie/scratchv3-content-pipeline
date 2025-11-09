"""
WordPress API endpoints for managing WordPress integration
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, List

from app.dependencies import get_current_active_user
from app.services.wordpress import wordpress_service

router = APIRouter()


class WordPressTestRequest(BaseModel):
    wordpress_url: str
    username: str
    password: str


class WordPressPostRequest(BaseModel):
    wordpress_url: str
    title: str
    content: str
    excerpt: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    featured_image_url: Optional[str] = None


class WordPressURLPresetRequest(BaseModel):
    url: str


class MarkdownTestRequest(BaseModel):
    content: str


@router.post("/test-connection")
async def test_wordpress_connection(
    request: WordPressTestRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Test connection to a WordPress site
    """
    result = await wordpress_service.test_connection(
        wordpress_url=request.wordpress_url,
        username=request.username,
        password=request.password
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/create-draft")
async def create_draft_post(
    request: WordPressPostRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Create a draft post in WordPress using user's saved credentials
    """
    user_settings = current_user.get("settings", {})
    
    # Get WordPress credentials from user settings
    username = user_settings.get("wordpress_app_username")
    password = user_settings.get("wordpress_app_password")
    
    if not username or not password:
        raise HTTPException(
            status_code=400, 
            detail="WordPress credentials not configured. Please set up your WordPress username and password in settings."
        )
    
    result = await wordpress_service.create_draft_post(
        wordpress_url=request.wordpress_url,
        username=username,
        password=password,
        title=request.title,
        content=request.content,
        excerpt=request.excerpt,
        categories=request.categories,
        tags=request.tags,
        featured_image_url=request.featured_image_url
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/url-presets")
async def get_wordpress_url_presets(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get user's WordPress URL presets
    """
    user_settings = current_user.get("settings", {})
    url_presets = user_settings.get("wordpress_url_presets", [])

    return {
        "presets": url_presets,
        "count": len(url_presets)
    }


@router.post("/test-markdown-conversion")
async def test_markdown_conversion(
    request: MarkdownTestRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Test markdown to HTML conversion for debugging formatting issues
    """
    result = wordpress_service.test_markdown_conversion(request.content)
    return result


@router.post("/create-draft-with-fallback")
async def create_draft_post_with_fallback(
    request: WordPressPostRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Create a draft post in WordPress with fallback formatting methods
    """
    user_settings = current_user.get("settings", {})

    # Get WordPress credentials from user settings
    username = user_settings.get("wordpress_app_username")
    password = user_settings.get("wordpress_app_password")

    if not username or not password:
        raise HTTPException(
            status_code=400,
            detail="WordPress credentials not configured. Please set up your WordPress username and password in settings."
        )

    result = await wordpress_service.create_draft_post_with_fallback(
        wordpress_url=request.wordpress_url,
        username=username,
        password=password,
        title=request.title,
        content=request.content,
        excerpt=request.excerpt,
        categories=request.categories,
        tags=request.tags,
        featured_image_url=request.featured_image_url
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/url-presets")
async def add_wordpress_url_preset(
    request: WordPressURLPresetRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Add a WordPress URL to presets
    """
    from app.services.auth import auth_service
    
    user_settings = current_user.get("settings", {})
    url_presets = user_settings.get("wordpress_url_presets", [])
    
    url = request.url.strip()
    if url not in url_presets:
        url_presets.append(url)
        user_settings["wordpress_url_presets"] = url_presets
        
        # Update user settings
        success = auth_service.update_user_settings(current_user["username"], user_settings)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update WordPress URL presets")
    
    return {
        "message": "WordPress URL preset added successfully",
        "url": url,
        "presets": url_presets
    }


@router.delete("/url-presets/{url}")
async def remove_wordpress_url_preset(
    url: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Remove a WordPress URL from presets
    """
    from app.services.auth import auth_service
    
    user_settings = current_user.get("settings", {})
    url_presets = user_settings.get("wordpress_url_presets", [])
    
    if url in url_presets:
        url_presets.remove(url)
        user_settings["wordpress_url_presets"] = url_presets
        
        # Update user settings
        success = auth_service.update_user_settings(current_user["username"], user_settings)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update WordPress URL presets")
    
    return {
        "message": "WordPress URL preset removed successfully",
        "url": url,
        "presets": url_presets
    }


@router.get("/site-info")
async def get_wordpress_site_info(
    wordpress_url: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get information about a WordPress site
    """
    user_settings = current_user.get("settings", {})
    
    # Get WordPress credentials from user settings
    username = user_settings.get("wordpress_app_username")
    password = user_settings.get("wordpress_app_password")
    
    if not username or not password:
        raise HTTPException(
            status_code=400, 
            detail="WordPress credentials not configured. Please set up your WordPress username and password in settings."
        )
    
    result = await wordpress_service.get_site_info(
        wordpress_url=wordpress_url,
        username=username,
        password=password
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result
