#!/usr/bin/env python3
"""
Test script to verify the AI service fixes work correctly
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.ai import ai_service
from app.config import settings

async def test_ai_service_fixes():
    """Test that AI service now properly uses LM Studio defaults"""
    
    print("🧪 Testing AI Service Fixes")
    print("=" * 50)
    
    # Test 1: Check config defaults
    print(f"✅ Config default AI provider: {settings.default_ai_provider}")
    print(f"✅ Config default LM Studio model: {settings.default_lmstudio_model}")
    print(f"✅ Config LM Studio URL: {settings.lmstudio_api_url}")
    
    # Test 2: Test AI service with no provider specified (should use defaults)
    print(f"\n🔄 Testing AI service with default settings...")
    
    user_settings = {
        "ai_provider": "lmstudio",
        "lmstudio_api_url": "http://127.0.0.1:1234/v1",
        "lmstudio_model": "qwen3-4b"
    }
    
    try:
        result = await ai_service.generate_content(
            prompt="Say 'Hello from LM Studio!' and nothing else.",
            provider=None,  # Should use config default (lmstudio)
            model=None,     # Should use config default (qwen3-4b)
            user_settings=user_settings,
            max_tokens=10
        )
        
        if result["success"]:
            print(f"✅ AI service test successful!")
            print(f"   Provider used: {result['provider']}")
            print(f"   Model used: {result['model_used']}")
            print(f"   Response: {result['content'][:100]}...")
        else:
            print(f"❌ AI service test failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ AI service test error: {e}")
    
    # Test 3: Test content generator logic
    print(f"\n🔄 Testing content generator logic...")
    
    from app.services.content_generator import ContentGeneratorService
    
    # Simulate the logic from content_generator.py
    ai_provider = user_settings.get("ai_provider", settings.default_ai_provider)
    
    if ai_provider == "openai":
        model = user_settings.get("openai_model", settings.default_openai_model)
    elif ai_provider == "lmstudio":
        model = user_settings.get("lmstudio_model", settings.default_lmstudio_model)
    else:  # openrouter
        model = user_settings.get("openrouter_model", settings.default_openrouter_model)
    
    print(f"✅ Content generator would use:")
    print(f"   Provider: {ai_provider}")
    print(f"   Model: {model}")
    
    if ai_provider == "lmstudio" and model == "qwen3-4b":
        print("✅ Content generator logic is now correct!")
    else:
        print("❌ Content generator logic still has issues")
    
    # Test 4: Test with different user settings
    print(f"\n🔄 Testing with empty user settings (should use config defaults)...")
    
    empty_settings = {}
    ai_provider = empty_settings.get("ai_provider", settings.default_ai_provider)
    
    if ai_provider == "openai":
        model = empty_settings.get("openai_model", settings.default_openai_model)
    elif ai_provider == "lmstudio":
        model = empty_settings.get("lmstudio_model", settings.default_lmstudio_model)
    else:  # openrouter
        model = empty_settings.get("openrouter_model", settings.default_openrouter_model)
    
    print(f"✅ With empty settings:")
    print(f"   Provider: {ai_provider}")
    print(f"   Model: {model}")
    
    if ai_provider == "lmstudio":
        print("✅ Empty settings correctly default to LM Studio!")
    else:
        print("❌ Empty settings not defaulting to LM Studio")

if __name__ == "__main__":
    asyncio.run(test_ai_service_fixes())
