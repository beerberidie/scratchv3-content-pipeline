# LM Studio Integration for ScratchV3

This document outlines the steps to integrate LM Studio as an AI provider alongside OpenAI and OpenRouter in the ScratchV3 content generation platform.

## Overview

LM Studio allows users to run AI models locally, which can reduce costs and provide more privacy compared to cloud-based solutions. This integration enables ScratchV3 to connect to a local LM Studio instance for content generation.

## Implementation Steps

### 1. Update AI Service

First, modify the AI service to support LM Studio:

```python
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
```

### 2. Update Client Selection Method

Add LM Studio to the `_get_client_and_model` method:

```python
def _get_client_and_model(self, provider: str, model: str, user_settings: Dict[str, Any]) -> tuple:
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
```

### 3. Add LM Studio Models

Update the `get_available_models` method to include LM Studio models:

```python
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
```

### 4. Update API Key Validation

Modify the `validate_api_key` method to handle LM Studio:

```python
async def validate_api_key(self, provider: str, api_key: str) -> Dict[str, Any]:
    """Validate API key for a provider"""
    
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
                model="local-model",  # Use the default model name
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return {"valid": True, "message": "LM Studio connection is valid"}
        
        else:
            return {"valid": False, "message": f"Unsupported provider: {provider}"}
    except Exception as e:
        return {"valid": False, "message": str(e)}
```

### 5. Update Configuration

Add LM Studio settings to the application configuration:

```python
# Default AI Settings
default_ai_provider: str = Field("openrouter", env="DEFAULT_AI_PROVIDER")
default_openai_model: str = Field("gpt-4", env="DEFAULT_OPENAI_MODEL")
default_openrouter_model: str = Field("google/gemini-2.0-flash-exp:free", env="DEFAULT_OPENROUTER_MODEL")
default_lmstudio_model: str = Field("local-model", env="DEFAULT_LMSTUDIO_MODEL")
lmstudio_api_url: str = Field("http://localhost:1234/v1", env="LMSTUDIO_API_URL")
```

### 6. Update Dashboard UI

Add LM Studio to the provider selection dropdown and create settings fields:

```html
<div class="form-group">
  <label>Primary AI Provider</label>
  <select id="aiProvider" onchange="updateProviderSettings()">
    <option value="openrouter">OpenRouter (Recommended)</option>
    <option value="openai">OpenAI</option>
    <option value="lmstudio">LM Studio (Local)</option>
  </select>
  <small class="form-help">Choose your preferred AI service for content generation</small>
</div>

<!-- LM Studio Settings -->
<div class="form-group" id="lmstudioSettingsGroup" style="display: none;">
  <label>LM Studio API URL</label>
  <input type="text" id="lmstudioApiUrl" placeholder="http://localhost:1234/v1" />
  <small class="form-help">Enter the URL for your local LM Studio API server</small>
  
  <label>LM Studio Model</label>
  <select id="lmstudioModel">
    <option value="local-model">Local Model</option>
    <option value="llama-3-8b">Llama 3 8B</option>
    <option value="mistral-7b">Mistral 7B</option>
    <option value="phi-2">Phi-2</option>
  </select>
  <small class="form-help">Select the model loaded in your LM Studio instance</small>
</div>
```

### 7. Update JavaScript

Modify the JavaScript to handle LM Studio provider selection:

```javascript
function updateProviderSettings() {
  const provider = document.getElementById('aiProvider').value;
  
  // Hide all provider-specific settings
  document.getElementById('openaiModelGroup').style.display = 'none';
  document.getElementById('openrouterModelGroup').style.display = 'none';
  document.getElementById('lmstudioSettingsGroup').style.display = 'none';
  
  // Show settings for selected provider
  if (provider === 'openai') {
    document.getElementById('openaiModelGroup').style.display = 'block';
  } else if (provider === 'openrouter') {
    document.getElementById('openrouterModelGroup').style.display = 'block';
  } else if (provider === 'lmstudio') {
    document.getElementById('lmstudioSettingsGroup').style.display = 'block';
  }
}

// Update settings with all required fields
const settingsData = {
  ai_provider: userSettings?.ai_provider || 'openrouter',
  openai_api_key: userSettings?.openai_api_key || undefined,
  openai_model: userSettings?.openai_model || 'gpt-4',
  openrouter_api_key: userSettings?.openrouter_api_key || undefined,
  openrouter_model: userSettings?.openrouter_model || 'google/gemini-2.0-flash-exp:free',
  lmstudio_api_url: userSettings?.lmstudio_api_url || 'http://localhost:1234/v1',
  lmstudio_model: userSettings?.lmstudio_model || 'local-model',
  pexels_api_key: userSettings?.pexels_api_key || undefined,
  wordpress_url_presets: updatedPresets,
  wordpress_app_username: userSettings?.wordpress_app_username || undefined,
  wordpress_app_password: userSettings?.wordpress_app_password || undefined
};
```

### 8. Update Environment Variables

Add LM Studio settings to the environment variables:

```
# Default AI Provider Settings
DEFAULT_AI_PROVIDER=openrouter
DEFAULT_OPENAI_MODEL=gpt-4
DEFAULT_OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
DEFAULT_LMSTUDIO_MODEL=local-model
LMSTUDIO_API_URL=http://localhost:1234/v1
```

## Setting Up LM Studio

1. Download and install LM Studio from [https://lmstudio.ai/](https://lmstudio.ai/)
2. Download a model (Llama 3, Mistral, Phi-2, etc.)
3. Start the local server in LM Studio (typically runs on http://localhost:1234)
4. Configure ScratchV3 to use the LM Studio URL

## Usage Notes

- LM Studio runs models locally on your machine, so performance depends on your hardware
- No API key is required for LM Studio, just the server URL
- The model must be loaded in LM Studio before ScratchV3 can use it
- For best results, use models with at least 7B parameters for content generation

## Troubleshooting

- If connection fails, ensure LM Studio server is running
- Check that the URL is correct (typically http://localhost:1234/v1)
- Verify that a model is loaded in LM Studio
- For large content generation tasks, increase the timeout settings

## Benefits of LM Studio Integration

- **Cost Savings**: No usage fees for API calls
- **Privacy**: Content generation happens locally
- **Offline Use**: Can generate content without internet connection
- **Customization**: Use any compatible model from Hugging Face
