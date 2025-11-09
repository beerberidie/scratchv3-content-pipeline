"""
Email API endpoints for sending generated content
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List

from app.dependencies import get_current_active_user
from app.services.email import email_service

router = APIRouter()


class SendEmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    content: str
    topic: Optional[str] = ""
    task_id: Optional[str] = None
    images: Optional[List[Dict[str, Any]]] = None


class TestSMTPRequest(BaseModel):
    host: str
    port: int
    username: str
    password: str
    from_email: EmailStr


@router.post("/send")
async def send_email(
    request: SendEmailRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Send email with generated content
    """
    user_settings = current_user.get("settings", {})
    
    result = await email_service.send_email(
        to_email=str(request.to_email),
        subject=request.subject,
        content=request.content,
        topic=request.topic,
        images=request.images,
        task_id=request.task_id,
        user_settings=user_settings
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/test-smtp")
async def test_smtp_connection(
    request: Optional[TestSMTPRequest] = None,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Test SMTP connection with provided settings or user's saved settings
    """
    user_settings = current_user.get("settings", {})
    
    # If request provided, use those settings for testing
    if request:
        test_settings = {
            "smtp_settings": {
                "host": request.host,
                "port": request.port,
                "username": request.username,
                "password": request.password,
                "from_email": str(request.from_email)
            }
        }
        result = await email_service.test_smtp_connection(test_settings)
    else:
        # Use user's saved settings
        result = await email_service.test_smtp_connection(user_settings)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/presets")
async def get_email_presets(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Get user's email presets
    """
    user_settings = current_user.get("settings", {})
    email_presets = user_settings.get("email_presets", [])
    
    return {
        "presets": email_presets,
        "count": len(email_presets)
    }


@router.post("/presets")
async def add_email_preset(
    email: EmailStr,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Add an email to presets
    """
    from app.services.auth import auth_service
    
    user_settings = current_user.get("settings", {})
    email_presets = user_settings.get("email_presets", [])
    
    email_str = str(email)
    if email_str not in email_presets:
        email_presets.append(email_str)
        user_settings["email_presets"] = email_presets
        
        # Update user settings
        success = auth_service.update_user_settings(current_user["username"], user_settings)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update email presets")
    
    return {
        "message": "Email preset added successfully",
        "email": email_str,
        "presets": email_presets
    }


@router.delete("/presets/{email}")
async def remove_email_preset(
    email: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Remove an email from presets
    """
    from app.services.auth import auth_service
    
    user_settings = current_user.get("settings", {})
    email_presets = user_settings.get("email_presets", [])
    
    if email in email_presets:
        email_presets.remove(email)
        user_settings["email_presets"] = email_presets
        
        # Update user settings
        success = auth_service.update_user_settings(current_user["username"], user_settings)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update email presets")
    
    return {
        "message": "Email preset removed successfully",
        "email": email,
        "presets": email_presets
    }
