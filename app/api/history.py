"""
History management API endpoints
"""
import re
import tempfile
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.dependencies import get_current_active_user
from app.services.storage import storage_service
from app.services.wordpress import wordpress_service

router = APIRouter()


def _clean_think_tags(text: str) -> str:
    """
    Remove <think></think> tags and their content from generated text.
    This ensures clean output for downloads.
    """
    if not text:
        return text

    # Remove <think></think> tags and everything between them
    # Use re.DOTALL flag to match newlines within think tags
    cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Clean up any extra whitespace left behind
    cleaned_text = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_text)  # Remove triple+ line breaks
    cleaned_text = cleaned_text.strip()

    return cleaned_text


class HistoryItem(BaseModel):
    model_config = {"protected_namespaces": ()}

    id: str
    task_id: str
    content_type: Optional[str] = None
    topic: Optional[str] = None
    content: str  # Changed from generated_content to match actual data structure
    images: List[str] = []  # Changed from image_urls to match actual data structure
    created_at: str
    email_sent: bool = False
    email_sent_at: Optional[str] = None
    # Additional fields that may be present in the data
    user_id: Optional[str] = None
    model_used: Optional[str] = None
    provider: Optional[str] = None
    tokens_used: Optional[int] = None
    generated_at: Optional[str] = None


@router.get("/", response_model=List[HistoryItem])
async def get_history(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get content generation history
    """
    history = storage_service.get_user_history(current_user["username"])
    return [HistoryItem(**item) for item in history]


@router.get("/{item_id}/download")
async def download_content(
    item_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Download generated content as a text file with proper image handling
    """
    item = storage_service.get_history_item(current_user["username"], item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        # Write header information
        f.write(f"Topic: {item.get('topic', 'N/A')}\n")
        f.write(f"Generated on: {item.get('created_at', 'N/A')}\n")
        f.write(f"Content Type: {item.get('content_type', 'blog')}\n")

        # Add model information if available
        if item.get('model_used'):
            f.write(f"AI Model: {item.get('model_used')} ({item.get('provider', 'Unknown')})\n")

        if item.get('tokens_used'):
            f.write(f"Tokens Used: {item.get('tokens_used')}\n")

        f.write("=" * 60 + "\n\n")

        # Write main content (support both field names for backward compatibility)
        content = item.get('content', item.get('generated_content', ''))
        if content:
            # Clean content by removing <think></think> tags before download
            cleaned_content = _clean_think_tags(content)
            f.write(cleaned_content)
        else:
            f.write("No content available")

        # Add image links if available with enhanced formatting
        images = item.get('images', item.get('image_urls', []))  # Support both field names
        if images:
            f.write("\n\n" + "=" * 60 + "\n")
            f.write(f"SUGGESTED IMAGES ({len(images)} available):\n")
            f.write("=" * 60 + "\n\n")

            for i, image in enumerate(images, 1):
                f.write(f"{i}. ")

                if isinstance(image, dict):
                    # Handle image object with metadata
                    image_url = image.get('url', image.get('src', 'No URL available'))
                    f.write(f"{image_url}\n")

                    # Add attribution if available
                    if image.get('attribution'):
                        f.write(f"   Attribution: {image['attribution']}\n")
                    elif image.get('photographer'):
                        photographer = image['photographer']
                        photographer_url = image.get('photographer_url', '')
                        if photographer_url:
                            f.write(f"   Photo by: {photographer} ({photographer_url})\n")
                        else:
                            f.write(f"   Photo by: {photographer}\n")

                    # Add alt text if available
                    if image.get('alt'):
                        f.write(f"   Description: {image['alt']}\n")

                    # Add search keywords if available
                    if image.get('search_keywords'):
                        keywords = image['search_keywords']
                        if isinstance(keywords, list):
                            f.write(f"   Keywords: {', '.join(keywords)}\n")
                        else:
                            f.write(f"   Keywords: {keywords}\n")

                    # Add thumbnail URL if different from main URL
                    if image.get('thumbnail') and image.get('thumbnail') != image_url:
                        f.write(f"   Thumbnail: {image['thumbnail']}\n")

                elif isinstance(image, str):
                    # Handle simple URL string
                    f.write(f"{image}\n")
                else:
                    # Handle unexpected format
                    f.write(f"{str(image)}\n")

                f.write("\n")  # Add spacing between images

            f.write("💡 TIP: Copy and paste these URLs into your browser to view the images.\n")
            f.write("📝 NOTE: Remember to provide proper attribution when using these images.\n\n")

        # Add footer
        f.write("=" * 60 + "\n")
        f.write("Generated by Scratch Automation App\n")
        f.write("For more information, visit: https://github.com/your-repo\n")
        f.write("=" * 60 + "\n")

        temp_path = f.name

    # Create a more descriptive filename
    topic_safe = item.get('topic', 'content').replace(' ', '_').replace('/', '_').replace('\\', '_')
    # Limit filename length and remove special characters
    topic_safe = re.sub(r'[^\w\-_.]', '', topic_safe)[:30]
    timestamp = item.get('created_at', '')[:10] if item.get('created_at') else 'unknown'
    filename = f"content_{timestamp}_{topic_safe}_{item_id[:8]}.txt"

    return FileResponse(
        temp_path,
        filename=filename,
        media_type='text/plain'
    )


@router.post("/{item_id}/re-post-wordpress")
async def re_post_to_wordpress(
    item_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Re-post content to WordPress
    """
    item = storage_service.get_history_item(current_user["username"], item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    # Get user settings for WordPress credentials
    user_settings = current_user.get("settings", {})
    username = user_settings.get("wordpress_app_username")
    password = user_settings.get("wordpress_app_password")

    if not username or not password:
        raise HTTPException(status_code=400, detail="WordPress credentials not configured")

    # Get WordPress URL presets
    url_presets = user_settings.get("wordpress_url_presets", [])
    if not url_presets:
        raise HTTPException(status_code=400, detail="No WordPress URL presets configured")

    # Use the first URL preset
    wordpress_url = url_presets[0]

    # Prepare content
    title = item.get("topic", "Untitled")
    content = item.get("content", "")

    # Add images to content if available
    images = item.get("images", [])
    if images:
        for image in images:
            if isinstance(image, dict) and image.get("url"):
                alt_text = image.get("alt", "Generated image")
                content += f'\n\n<img src="{image["url"]}" alt="{alt_text}" />'
            elif isinstance(image, str):
                content += f'\n\n<img src="{image}" alt="Generated image" />'

    # Post to WordPress
    result = await wordpress_service.create_draft_post(
        wordpress_url=wordpress_url,
        username=username,
        password=password,
        title=title,
        content=content
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "message": "Content re-posted to WordPress successfully",
        "item_id": item_id,
        "wordpress_post": result.get("post", {})
    }


@router.post("/{item_id}/re-email")
async def re_email_content(
    item_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Re-send content via email
    """
    item = storage_service.get_history_item(current_user["username"], item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    # TODO: Implement actual re-email functionality
    # For now, just return success message
    return {"message": "Content re-sent successfully", "item_id": item_id}


@router.post("/{item_id}/share")
async def share_content(
    item_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Generate shareable link for content
    """
    item = storage_service.get_history_item(current_user["username"], item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    # TODO: Implement actual sharing functionality
    # For now, return a placeholder URL
    return {
        "share_url": f"https://scratch.local/shared/{item_id}",
        "expires_at": "2025-07-19T10:00:00Z",
        "item_id": item_id
    }


@router.delete("/{item_id}")
async def delete_content(
    item_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Delete content from history
    """
    success = storage_service.delete_history_item(current_user["username"], item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Content not found")

    return {"message": "Content deleted successfully"}
