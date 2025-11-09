"""
Image search and management API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.dependencies import get_current_active_user
from app.services.images import image_service

router = APIRouter()


class ImageSearchRequest(BaseModel):
    query: str
    per_page: int = 15
    page: int = 1
    orientation: str = "all"  # all, landscape, portrait, square
    size: str = "all"  # all, large, medium, small


class ImagePhoto(BaseModel):
    id: int
    url: str
    photographer: str
    photographer_url: str
    src: Dict[str, str]
    width: int
    height: int
    alt: str
    avg_color: str


class ImageSearchResponse(BaseModel):
    success: bool
    total_results: int
    page: int
    per_page: int
    photos: list[ImagePhoto]
    next_page: str
    prev_page: str
    error: Optional[str] = None


class TestImageAPIKeyRequest(BaseModel):
    api_key: str


@router.get("/search", response_model=ImageSearchResponse)
async def search_images(
    query: str = Query(..., description="Search query for images"),
    per_page: int = Query(15, ge=1, le=80, description="Number of images per page"),
    page: int = Query(1, ge=1, description="Page number"),
    orientation: str = Query("all", description="Image orientation"),
    size: str = Query("all", description="Image size"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Search for images using Pexels API
    """
    user_settings = current_user.get("settings", {})
    
    result = await image_service.search_images(
        query=query,
        per_page=per_page,
        page=page,
        orientation=orientation,
        size=size,
        user_settings=user_settings
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Image search failed"))
    
    return ImageSearchResponse(**result)


@router.post("/search", response_model=ImageSearchResponse)
async def search_images_post(
    request: ImageSearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Search for images using POST request (for complex queries)
    """
    user_settings = current_user.get("settings", {})
    
    result = await image_service.search_images(
        query=request.query,
        per_page=request.per_page,
        page=request.page,
        orientation=request.orientation,
        size=request.size,
        user_settings=user_settings
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Image search failed"))
    
    return ImageSearchResponse(**result)


@router.get("/curated")
async def get_curated_images(
    per_page: int = Query(15, ge=1, le=80, description="Number of images per page"),
    page: int = Query(1, ge=1, description="Page number"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get curated images from Pexels
    """
    user_settings = current_user.get("settings", {})
    
    result = await image_service.get_curated_images(
        per_page=per_page,
        page=page,
        user_settings=user_settings
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to get curated images"))
    
    return result


@router.get("/{image_id}")
async def get_image_by_id(
    image_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get a specific image by ID
    """
    user_settings = current_user.get("settings", {})
    
    result = await image_service.get_image_by_id(
        image_id=image_id,
        user_settings=user_settings
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error", "Image not found"))
    
    return result


@router.post("/test-api-key")
async def test_pexels_api_key(request: TestImageAPIKeyRequest):
    """
    Test if a Pexels API key is valid
    """
    result = await image_service.test_api_key(request.api_key)
    return result


@router.get("/{image_id}/attribution")
async def get_image_attribution(
    image_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get proper attribution text for an image
    """
    user_settings = current_user.get("settings", {})
    
    result = await image_service.get_image_by_id(
        image_id=image_id,
        user_settings=user_settings
    )
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail="Image not found")
    
    attribution = image_service.get_attribution_text(result["photo"])
    
    return {
        "image_id": image_id,
        "attribution": attribution,
        "photographer": result["photo"].get("photographer"),
        "photographer_url": result["photo"].get("photographer_url")
    }
