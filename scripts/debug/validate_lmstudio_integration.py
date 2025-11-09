#!/usr/bin/env python3
"""
Validation script for LM Studio integration
"""
import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai import AIService
from app.config import settings


async def validate_lmstudio_integration():
    """Validate LM Studio integration"""
    print("🔍 Validating LM Studio Integration...")
    print("=" * 50)
    
    # Initialize AI service
    ai_service = AIService()
    
    # Test 1: Check if LM Studio client can be initialized
    print("\n1. Testing LM Studio client initialization...")
    try:
        # Temporarily set LM Studio URL for testing
        original_url = settings.lmstudio_api_url
        settings.lmstudio_api_url = "http://localhost:1234/v1"
        
        ai_service._initialize_clients()
        
        if ai_service.lmstudio_client is not None:
            print("✅ LM Studio client initialized successfully")
        else:
            print("❌ LM Studio client not initialized")
            
        # Restore original URL
        settings.lmstudio_api_url = original_url
        
    except Exception as e:
        print(f"❌ Error initializing LM Studio client: {e}")
    
    # Test 2: Check _get_client_and_model method
    print("\n2. Testing _get_client_and_model method...")
    try:
        user_settings = {"lmstudio_api_url": "http://localhost:1234/v1"}
        client, model = ai_service._get_client_and_model("lmstudio", "local-model", user_settings)
        
        if client is not None and model == "local-model":
            print("✅ _get_client_and_model works for LM Studio")
        else:
            print("❌ _get_client_and_model failed for LM Studio")
            
    except Exception as e:
        print(f"❌ Error in _get_client_and_model: {e}")
    
    # Test 3: Check available models
    print("\n3. Testing get_available_models...")
    try:
        models = await ai_service.get_available_models("lmstudio")
        
        if len(models) > 0:
            print(f"✅ Found {len(models)} LM Studio models:")
            for model in models:
                print(f"   - {model['id']}: {model['name']}")
        else:
            print("❌ No LM Studio models found")
            
    except Exception as e:
        print(f"❌ Error getting available models: {e}")
    
    # Test 4: Check unsupported provider handling
    print("\n4. Testing unsupported provider handling...")
    try:
        ai_service._get_client_and_model("unsupported", "model", {})
        print("❌ Should have raised ValueError for unsupported provider")
    except ValueError as e:
        if "Unsupported provider" in str(e):
            print("✅ Correctly handles unsupported provider")
        else:
            print(f"❌ Unexpected error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error type: {e}")
    
    # Test 5: Check missing LM Studio URL handling
    print("\n5. Testing missing LM Studio URL handling...")
    try:
        user_settings = {}
        original_url = settings.lmstudio_api_url
        settings.lmstudio_api_url = None
        
        ai_service._get_client_and_model("lmstudio", "local-model", user_settings)
        print("❌ Should have raised ValueError for missing LM Studio URL")
        
    except ValueError as e:
        if "LM Studio API URL not configured" in str(e):
            print("✅ Correctly handles missing LM Studio URL")
        else:
            print(f"❌ Unexpected error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error type: {e}")
    finally:
        settings.lmstudio_api_url = original_url
    
    print("\n" + "=" * 50)
    print("🎉 LM Studio integration validation complete!")
    print("\nNext steps:")
    print("1. Start LM Studio and load a model")
    print("2. Configure the LM Studio API URL in the dashboard")
    print("3. Test content generation with LM Studio")


if __name__ == "__main__":
    asyncio.run(validate_lmstudio_integration())
