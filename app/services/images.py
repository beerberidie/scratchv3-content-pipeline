"""
Image service for searching and retrieving images from Pexels API
"""
import httpx
from typing import Dict, Any, List, Optional
import asyncio

from app.config import settings


class ImageService:
    """Service for image search and retrieval"""
    
    def __init__(self):
        self.base_url = "https://api.pexels.com/v1"
        self.headers = {}
        if settings.pexels_api_key:
            self.headers["Authorization"] = settings.pexels_api_key
    
    def _get_headers(self, user_settings: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Get headers with API key from user settings or global config"""
        headers = {"Authorization": ""}
        
        # Use user's API key if available, otherwise global
        if user_settings and user_settings.get("pexels_api_key"):
            headers["Authorization"] = user_settings["pexels_api_key"]
        elif settings.pexels_api_key:
            headers["Authorization"] = settings.pexels_api_key
        else:
            raise ValueError("Pexels API key not configured")
        
        return headers
    
    async def search_images(
        self,
        query: str,
        per_page: int = 15,
        page: int = 1,
        orientation: str = "all",  # all, landscape, portrait, square
        size: str = "all",  # all, large, medium, small
        user_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for images using Pexels API"""
        
        try:
            headers = self._get_headers(user_settings)
            
            params = {
                "query": query,
                "per_page": min(per_page, 80),  # Pexels max is 80
                "page": page,
                "orientation": orientation,
                "size": size
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    headers=headers,
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Process and format the response
                    formatted_photos = []
                    for photo in data.get("photos", []):
                        formatted_photos.append({
                            "id": photo["id"],
                            "url": photo["url"],
                            "photographer": photo["photographer"],
                            "photographer_url": photo["photographer_url"],
                            "src": {
                                "original": photo["src"]["original"],
                                "large": photo["src"]["large"],
                                "large2x": photo["src"]["large2x"],
                                "medium": photo["src"]["medium"],
                                "small": photo["src"]["small"],
                                "portrait": photo["src"]["portrait"],
                                "landscape": photo["src"]["landscape"],
                                "tiny": photo["src"]["tiny"]
                            },
                            "width": photo["width"],
                            "height": photo["height"],
                            "alt": photo.get("alt", ""),
                            "avg_color": photo.get("avg_color", "#000000")
                        })
                    
                    return {
                        "success": True,
                        "total_results": data.get("total_results", 0),
                        "page": data.get("page", 1),
                        "per_page": data.get("per_page", 15),
                        "photos": formatted_photos,
                        "next_page": data.get("next_page", ""),
                        "prev_page": data.get("prev_page", "")
                    }
                
                elif response.status_code == 429:
                    return {
                        "success": False,
                        "error": "Rate limit exceeded. Please try again later.",
                        "photos": []
                    }
                
                elif response.status_code == 401:
                    return {
                        "success": False,
                        "error": "Invalid API key. Please check your Pexels API key.",
                        "photos": []
                    }
                
                else:
                    return {
                        "success": False,
                        "error": f"API request failed with status {response.status_code}",
                        "photos": []
                    }
                    
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timeout. Please try again.",
                "photos": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Image search failed: {str(e)}",
                "photos": []
            }
    
    async def get_curated_images(
        self,
        per_page: int = 15,
        page: int = 1,
        user_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get curated images from Pexels"""
        
        try:
            headers = self._get_headers(user_settings)
            
            params = {
                "per_page": min(per_page, 80),
                "page": page
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/curated",
                    headers=headers,
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "photos": data.get("photos", []),
                        "page": data.get("page", 1),
                        "per_page": data.get("per_page", 15),
                        "next_page": data.get("next_page", ""),
                        "prev_page": data.get("prev_page", "")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get curated images: {response.status_code}",
                        "photos": []
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get curated images: {str(e)}",
                "photos": []
            }
    
    async def get_image_by_id(
        self,
        image_id: int,
        user_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get a specific image by ID"""
        
        try:
            headers = self._get_headers(user_settings)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/photos/{image_id}",
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    photo = response.json()
                    return {
                        "success": True,
                        "photo": photo
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Image not found: {response.status_code}",
                        "photo": None
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get image: {str(e)}",
                "photo": None
            }
    
    async def test_api_key(self, api_key: str) -> Dict[str, Any]:
        """Test if a Pexels API key is valid"""
        
        try:
            headers = {"Authorization": api_key}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/curated",
                    headers=headers,
                    params={"per_page": 1},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return {"valid": True, "message": "API key is valid"}
                elif response.status_code == 401:
                    return {"valid": False, "message": "Invalid API key"}
                else:
                    return {"valid": False, "message": f"API test failed: {response.status_code}"}
                    
        except Exception as e:
            return {"valid": False, "message": f"API key test failed: {str(e)}"}
    
    def get_attribution_text(self, photo: Dict[str, Any]) -> str:
        """Generate proper attribution text for a photo"""
        photographer = photo.get("photographer", "Unknown")
        photographer_url = photo.get("photographer_url", "")
        
        if photographer_url:
            return f"Photo by {photographer} on Pexels ({photographer_url})"
        else:
            return f"Photo by {photographer} on Pexels"


# Global image service instance
image_service = ImageService()
