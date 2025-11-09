"""
AI service for content generation using OpenAI, OpenRouter, and LM Studio APIs
"""
import asyncio
import json
from typing import Dict, Any, List, Optional, AsyncGenerator
import httpx
from openai import AsyncOpenAI

from app.config import settings
from app.api.keys import get_decrypted_key


class AIService:
    """AI service for content generation"""
    
    def __init__(self):
        self.openai_client = None
        self.openrouter_client = None
        self.lmstudio_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI clients"""
        # OpenAI client
        if settings.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

        # OpenRouter client (uses OpenAI-compatible interface)
        if settings.openrouter_api_key:
            self.openrouter_client = AsyncOpenAI(
                api_key=settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1"
            )

        # LM Studio client (uses OpenAI-compatible interface)
        if settings.lmstudio_api_url:
            self.lmstudio_client = AsyncOpenAI(
                api_key="not-needed",  # LM Studio typically doesn't require an API key
                base_url=settings.lmstudio_api_url
            )
    
    def _get_client_and_model(self, provider: str, model: str, user_settings: Dict[str, Any]):
        """Get the appropriate client and model based on provider"""
        if provider == "openai":
            # Use user's API key if available, otherwise global
            api_key = self._get_user_api_key("openai", user_settings) or settings.openai_api_key
            if not api_key:
                raise ValueError("OpenAI API key not configured")

            client = AsyncOpenAI(api_key=api_key)
            return client, model

        elif provider == "openrouter":
            # Use user's API key if available, otherwise global
            api_key = self._get_user_api_key("openrouter", user_settings) or settings.openrouter_api_key
            if not api_key:
                raise ValueError("OpenRouter API key not configured")

            client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            return client, model

        elif provider == "lmstudio":
            # Get LM Studio URL from user settings or global settings
            lmstudio_url = user_settings.get("lmstudio_api_url") or settings.lmstudio_api_url
            if not lmstudio_url:
                raise ValueError("LM Studio API URL not configured")

            client = AsyncOpenAI(
                api_key="not-needed",  # LM Studio typically doesn't require an API key
                base_url=lmstudio_url
            )
            return client, model

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _get_user_api_key(self, provider: str, user_settings: Dict[str, Any]) -> Optional[str]:
        """Get user API key from either new encrypted system or legacy system"""
        # First try to get user_id from user_settings
        user_id = user_settings.get("user_id")

        # If we don't have user_id, try to extract from common patterns
        if not user_id:
            user_id = user_settings.get("email") or user_settings.get("username")

        # Try new encrypted system first
        if user_id:
            encrypted_key = get_decrypted_key(user_id, provider)
            if encrypted_key:
                return encrypted_key

        # Fall back to legacy system (users.json)
        legacy_key_field = f"{provider}_api_key"
        return user_settings.get(legacy_key_field)
    
    async def generate_content(
        self,
        prompt: str,
        provider: str = None,
        model: str = None,
        user_settings: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate content using specified AI provider"""

        user_settings = user_settings or {}

        # Use config defaults if not specified
        if provider is None:
            provider = settings.default_ai_provider
        if model is None:
            if provider == "openai":
                model = settings.default_openai_model
            elif provider == "lmstudio":
                model = settings.default_lmstudio_model
            else:  # openrouter
                model = settings.default_openrouter_model

        try:
            client, model_name = self._get_client_and_model(provider, model, user_settings)

            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Make API call
            response = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            # Extract response data
            content = response.choices[0].message.content
            usage = response.usage

            return {
                "content": content,
                "model_used": model_name,
                "provider": provider,
                "tokens_used": usage.total_tokens if usage else 0,
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "success": True
            }

        except Exception as e:
            return {
                "content": "",
                "model_used": model,
                "provider": provider,
                "tokens_used": 0,
                "error": str(e),
                "success": False
            }

    async def generate_content_with_messages(
        self,
        messages: List[Dict[str, str]],
        provider: str = None,
        model: str = None,
        user_settings: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate content using pre-built messages array"""

        user_settings = user_settings or {}

        # Use config defaults if not specified
        if provider is None:
            provider = settings.default_ai_provider
        if model is None:
            if provider == "openai":
                model = settings.default_openai_model
            elif provider == "lmstudio":
                model = settings.default_lmstudio_model
            else:  # openrouter
                model = settings.default_openrouter_model

        try:
            client, model_name = self._get_client_and_model(provider, model, user_settings)

            # Make API call with provided messages
            response = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            # Extract response data
            content = response.choices[0].message.content
            usage = response.usage

            return {
                "content": content,
                "model_used": model_name,
                "provider": provider,
                "tokens_used": usage.total_tokens if usage else 0,
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "success": True
            }

        except Exception as e:
            return {
                "content": "",
                "model_used": model,
                "provider": provider,
                "tokens_used": 0,
                "error": str(e),
                "success": False
            }
    
    async def generate_content_stream(
        self,
        prompt: str,
        provider: str = None,
        model: str = None,
        user_settings: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate content with streaming response"""

        user_settings = user_settings or {}

        # Use config defaults if not specified
        if provider is None:
            provider = settings.default_ai_provider
        if model is None:
            if provider == "openai":
                model = settings.default_openai_model
            elif provider == "lmstudio":
                model = settings.default_lmstudio_model
            else:  # openrouter
                model = settings.default_openrouter_model

        try:
            client, model_name = self._get_client_and_model(provider, model, user_settings)
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Make streaming API call
            stream = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield {
                        "content": chunk.choices[0].delta.content,
                        "model_used": model_name,
                        "provider": provider,
                        "is_complete": False,
                        "success": True
                    }
            
            # Send completion signal
            yield {
                "content": "",
                "model_used": model_name,
                "provider": provider,
                "is_complete": True,
                "success": True
            }
            
        except Exception as e:
            yield {
                "content": "",
                "model_used": model,
                "provider": provider,
                "error": str(e),
                "is_complete": True,
                "success": False
            }
    
    async def get_available_models(self, provider: str, user_settings: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """Get available models for a provider"""

        user_settings = user_settings or {}

        if provider == "openai":
            return [
                {"id": "gpt-4", "name": "GPT-4"},
                {"id": "gpt-4-turbo-preview", "name": "GPT-4 Turbo"},
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
                {"id": "gpt-3.5-turbo-16k", "name": "GPT-3.5 Turbo 16K"}
            ]

        elif provider == "openrouter":
            # Static list of free OpenRouter models only
            return [
                {"id": "google/gemini-2.0-flash-exp:free", "name": "Gemini 2.0 Flash (Free)"},
                {"id": "meta-llama/llama-3.1-8b-instruct:free", "name": "Llama 3.1 8B (Free)"},
                {"id": "meta-llama/llama-3.2-3b-instruct:free", "name": "Llama 3.2 3B (Free)"},
                {"id": "meta-llama/llama-3.2-1b-instruct:free", "name": "Llama 3.2 1B (Free)"},
                {"id": "google/gemini-flash-1.5:free", "name": "Gemini Flash 1.5 (Free)"},
                {"id": "microsoft/phi-3-mini-128k-instruct:free", "name": "Phi-3 Mini (Free)"},
                {"id": "microsoft/phi-3-medium-128k-instruct:free", "name": "Phi-3 Medium (Free)"}
            ]

        elif provider == "lmstudio":
            # For LM Studio, we'll provide a default list
            # In a real implementation, you might want to query the LM Studio API
            # to get the actual available models
            return [
                {"id": "local-model", "name": "Local Model"},
                {"id": "llama-3-8b", "name": "Llama 3 8B"},
                {"id": "mistral-7b", "name": "Mistral 7B"},
                {"id": "phi-2", "name": "Phi-2"}
            ]

        else:
            return []
    
    async def test_api_key(self, provider: str, api_key: str) -> Dict[str, Any]:
        """Test if an API key is valid"""

        try:
            if provider == "openai":
                client = AsyncOpenAI(api_key=api_key)
                # Test with a simple completion
                response = await client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                return {"valid": True, "message": "API key is valid"}

            elif provider == "openrouter":
                client = AsyncOpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                # Test with a simple completion
                response = await client.chat.completions.create(
                    model="google/gemini-2.0-flash-exp:free",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                return {"valid": True, "message": "API key is valid"}

            elif provider == "lmstudio":
                # For LM Studio, we validate the URL rather than an API key
                client = AsyncOpenAI(
                    api_key="not-needed",
                    base_url=api_key  # In this case, api_key is actually the URL
                )
                # Test with a simple completion
                response = await client.chat.completions.create(
                    model="qwen3-4b",  # Use the default model name
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                return {"valid": True, "message": "LM Studio connection is valid"}

            else:
                return {"valid": False, "message": f"Unsupported provider: {provider}"}

        except Exception as e:
            return {"valid": False, "message": f"API key test failed: {str(e)}"}

    async def get_lmstudio_models(self, api_url: str) -> Dict[str, Any]:
        """Get available models from LM Studio"""
        try:
            client = AsyncOpenAI(
                api_key="not-needed",
                base_url=api_url
            )

            # Get list of available models
            models = await client.models.list()
            model_list = [model.id for model in models.data]

            return {
                "success": True,
                "models": model_list,
                "message": f"Found {len(model_list)} models"
            }

        except Exception as e:
            return {
                "success": False,
                "models": [],
                "message": f"Failed to fetch models: {str(e)}"
            }


# Global AI service instance
ai_service = AIService()
