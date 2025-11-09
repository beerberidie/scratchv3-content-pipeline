"""
Content generation API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json

from app.dependencies import get_current_active_user
from app.services.ai import ai_service

router = APIRouter()


class GenerateRequest(BaseModel):
    prompt: str
    ai_provider: str = "openrouter"
    model: str = "google/gemini-2.0-flash-exp:free"
    max_tokens: int = 2000
    temperature: float = 0.7
    system_prompt: Optional[str] = None


class GenerateResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    content: str
    model_used: str
    provider: str
    tokens_used: int
    prompt_tokens: int
    completion_tokens: int
    success: bool
    error: Optional[str] = None


class TestAPIKeyRequest(BaseModel):
    provider: str
    api_key: str


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(
    request: GenerateRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Generate content using AI
    """
    user_settings = current_user.get("settings", {})

    result = await ai_service.generate_content(
        prompt=request.prompt,
        provider=request.ai_provider,
        model=request.model,
        user_settings=user_settings,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        system_prompt=request.system_prompt
    )

    return GenerateResponse(**result)


@router.post("/generate/stream")
async def generate_content_stream(
    request: GenerateRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Generate content using AI with streaming response
    """
    user_settings = current_user.get("settings", {})

    async def stream_generator():
        async for chunk in ai_service.generate_content_stream(
            prompt=request.prompt,
            provider=request.ai_provider,
            model=request.model,
            user_settings=user_settings,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system_prompt=request.system_prompt
        ):
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(
        stream_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/models/{provider}")
async def get_available_models(
    provider: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get available models for a specific AI provider
    """
    user_settings = current_user.get("settings", {})
    models = await ai_service.get_available_models(provider, user_settings)

    if not models:
        raise HTTPException(status_code=404, detail="Provider not found or no models available")

    return {"models": models}


@router.post("/test-api-key")
async def test_api_key(request: TestAPIKeyRequest):
    """
    Test if an API key is valid
    """
    result = await ai_service.test_api_key(request.provider, request.api_key)
    return result


@router.post("/generate-article")
async def generate_article(
    request: GenerateRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Generate a full article with structured content
    """
    user_settings = current_user.get("settings", {})

    # Enhanced system prompt for article generation
    article_system_prompt = """You are a professional content writer. Generate well-structured, engaging articles that include:

    1. A compelling headline
    2. An engaging introduction
    3. Well-organized body sections with subheadings
    4. A strong conclusion
    5. Proper formatting with markdown

    Make the content informative, engaging, and suitable for publication. Use a professional yet accessible tone."""

    result = await ai_service.generate_content(
        prompt=request.prompt,
        provider=request.ai_provider,
        model=request.model,
        user_settings=user_settings,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        system_prompt=article_system_prompt
    )

    return GenerateResponse(**result)


@router.post("/generate-social-post")
async def generate_social_post(
    request: GenerateRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Generate social media post content
    """
    user_settings = current_user.get("settings", {})

    # System prompt for social media content
    social_system_prompt = """You are a social media content creator. Generate engaging, concise social media posts that:

    1. Are attention-grabbing and shareable
    2. Include relevant hashtags
    3. Are optimized for engagement
    4. Match the platform's best practices
    5. Include a clear call-to-action when appropriate

    Keep the tone conversational and engaging while maintaining professionalism."""

    result = await ai_service.generate_content(
        prompt=request.prompt,
        provider=request.ai_provider,
        model=request.model,
        user_settings=user_settings,
        max_tokens=min(request.max_tokens, 500),  # Shorter for social posts
        temperature=request.temperature,
        system_prompt=social_system_prompt
    )

    return GenerateResponse(**result)
