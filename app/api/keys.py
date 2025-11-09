"""
API Key Management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import base64
from cryptography.fernet import Fernet

from app.dependencies import get_current_active_user
from app.services.storage import storage_service

router = APIRouter()


class KeyRequest(BaseModel):
    provider: str
    key: str


class KeyStatusResponse(BaseModel):
    openai: bool = False
    openrouter: bool = False
    pexels: bool = False


def get_encryption_key() -> bytes:
    """Get or create encryption key for API keys"""
    # In production, this should be stored securely (environment variable, key management service)
    # For now, we'll use a simple approach
    import os
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        # Generate a key for development (not secure for production)
        key = Fernet.generate_key()
        os.environ['ENCRYPTION_KEY'] = key.decode()
    else:
        key = key.encode()
    return key


def encrypt_key(api_key: str) -> str:
    """Encrypt an API key for storage"""
    f = Fernet(get_encryption_key())
    encrypted = f.encrypt(api_key.encode())
    return base64.b64encode(encrypted).decode()


def decrypt_key(encrypted_key: str) -> str:
    """Decrypt an API key from storage"""
    f = Fernet(get_encryption_key())
    encrypted_bytes = base64.b64decode(encrypted_key.encode())
    decrypted = f.decrypt(encrypted_bytes)
    return decrypted.decode()


@router.get("/status", response_model=KeyStatusResponse)
async def get_keys_status(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get the status of API keys for the current user
    Returns boolean status for each provider
    """
    user_id = current_user["email"]

    try:
        # First check new encrypted storage system
        user_keys = storage_service.get_user_keys(user_id)

        status = KeyStatusResponse()

        # Check each provider in new system
        for provider_key in user_keys:
            provider = provider_key.get("provider")
            has_key = bool(provider_key.get("key_encrypted"))

            if provider == "openai":
                status.openai = has_key
            elif provider == "openrouter":
                status.openrouter = has_key
            elif provider == "pexels":
                status.pexels = has_key

        # If no keys found in new system, check legacy system (users.json)
        if not status.openai and not status.openrouter and not status.pexels:
            user_settings = current_user.get("settings", {})

            if user_settings:
                status.openai = bool(user_settings.get("openai_api_key"))
                status.openrouter = bool(user_settings.get("openrouter_api_key"))
                status.pexels = bool(user_settings.get("pexels_api_key"))

        return status

    except Exception as e:
        # Return all False if there's an error
        return KeyStatusResponse()


@router.post("/")
async def upsert_api_key(
    request: KeyRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Add or update an API key for a provider
    """
    user_id = current_user["email"]
    
    # Validate provider
    valid_providers = ["openai", "openrouter", "pexels"]
    if request.provider not in valid_providers:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
        )
    
    # Validate key format (basic validation)
    if not request.key or len(request.key.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="API key must be at least 10 characters long"
        )
    
    try:
        # Encrypt the key
        encrypted_key = encrypt_key(request.key.strip())
        
        # Store the encrypted key
        storage_service.upsert_user_key(
            user_id=user_id,
            provider=request.provider,
            encrypted_key=encrypted_key
        )
        
        # Return updated status
        status_response = await get_keys_status(current_user)
        
        return {
            "success": True,
            "message": f"{request.provider.title()} API key saved successfully",
            "status": status_response
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save API key: {str(e)}"
        )


@router.delete("/{provider}")
async def delete_api_key(
    provider: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Delete an API key for a provider
    """
    user_id = current_user["email"]
    
    # Validate provider
    valid_providers = ["openai", "openrouter", "pexels"]
    if provider not in valid_providers:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
        )
    
    try:
        # Delete the key
        storage_service.delete_user_key(user_id, provider)
        
        # Return updated status
        status_response = await get_keys_status(current_user)
        
        return {
            "success": True,
            "message": f"{provider.title()} API key deleted successfully",
            "status": status_response
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete API key: {str(e)}"
        )


@router.get("/{provider}")
async def get_api_key(
    provider: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get a decrypted API key for a provider (for internal use)
    Returns masked key for security
    """
    user_id = current_user["email"]
    
    # Validate provider
    valid_providers = ["openai", "openrouter", "pexels"]
    if provider not in valid_providers:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
        )
    
    try:
        # Get the encrypted key
        user_key = storage_service.get_user_key(user_id, provider)
        
        if not user_key or not user_key.get("key_encrypted"):
            raise HTTPException(
                status_code=404,
                detail=f"No API key found for {provider}"
            )
        
        # Decrypt the key
        decrypted_key = decrypt_key(user_key["key_encrypted"])
        
        # Return masked version for security
        if len(decrypted_key) > 8:
            masked_key = decrypted_key[:4] + "*" * (len(decrypted_key) - 8) + decrypted_key[-4:]
        else:
            masked_key = "*" * len(decrypted_key)
        
        return {
            "provider": provider,
            "key_masked": masked_key,
            "has_key": True,
            "created_at": user_key.get("created_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve API key: {str(e)}"
        )


def get_decrypted_key(user_id: str, provider: str) -> Optional[str]:
    """
    Internal function to get decrypted API key for use by other services
    """
    try:
        user_key = storage_service.get_user_key(user_id, provider)
        if user_key and user_key.get("key_encrypted"):
            return decrypt_key(user_key["key_encrypted"])
        return None
    except Exception:
        return None
