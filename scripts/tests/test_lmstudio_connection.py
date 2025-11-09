#!/usr/bin/env python3
"""
Test script to verify LM Studio connection
"""
import asyncio
import httpx
from openai import AsyncOpenAI

async def test_lmstudio_connection():
    """Test LM Studio connection and endpoints"""
    
    base_urls = [
        "http://localhost:1234/v1",
        "http://localhost:1234",
        "http://127.0.0.1:1234/v1",
        "http://127.0.0.1:1234"
    ]
    
    print("🔍 Testing LM Studio connection...")
    print("=" * 50)
    
    for base_url in base_urls:
        print(f"\n📡 Testing: {base_url}")
        
        # Test basic connectivity
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{base_url}/models")
                print(f"   ✅ Models endpoint: {response.status_code}")
                if response.status_code == 200:
                    models = response.json()
                    print(f"   📋 Available models: {len(models.get('data', []))}")
                    for model in models.get('data', [])[:3]:  # Show first 3 models
                        print(f"      - {model.get('id', 'Unknown')}")
        except Exception as e:
            print(f"   ❌ Models endpoint failed: {e}")
        
        # Test chat completions endpoint
        try:
            client = AsyncOpenAI(
                api_key="not-needed",
                base_url=base_url
            )
            
            response = await client.chat.completions.create(
                model="qwen3-4b",  # Try default model
                messages=[{"role": "user", "content": "Hello, respond with just 'Hi'"}],
                max_tokens=5,
                timeout=30.0
            )
            print(f"   ✅ Chat completions: Working!")
            print(f"   💬 Response: {response.choices[0].message.content}")
            return base_url  # Return working URL
            
        except Exception as e:
            print(f"   ❌ Chat completions failed: {e}")
    
    print("\n❌ No working LM Studio connection found!")
    print("\n🔧 Troubleshooting steps:")
    print("1. Ensure LM Studio is installed and running")
    print("2. Load a model in LM Studio")
    print("3. Start the local server in LM Studio")
    print("4. Check that the server is running on port 1234")
    print("5. Try different model names if 'qwen3-4b' doesn't work")
    
    return None

async def test_specific_models():
    """Test with different model names"""
    
    model_names = [
        "qwen3-4b",
        "local-model", 
        "llama-3-8b",
        "mistral-7b",
        "phi-2"
    ]
    
    base_url = "http://localhost:1234/v1"
    
    print(f"\n🧪 Testing different model names with {base_url}")
    print("=" * 50)
    
    for model_name in model_names:
        try:
            client = AsyncOpenAI(
                api_key="not-needed",
                base_url=base_url
            )
            
            response = await client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=3,
                timeout=15.0
            )
            print(f"   ✅ Model '{model_name}': Working!")
            return model_name
            
        except Exception as e:
            print(f"   ❌ Model '{model_name}': {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 LM Studio Connection Test")
    print("=" * 50)
    
    # Test connection
    working_url = asyncio.run(test_lmstudio_connection())
    
    if working_url:
        print(f"\n✅ Found working LM Studio at: {working_url}")
        
        # Test models
        working_model = asyncio.run(test_specific_models())
        
        if working_model:
            print(f"\n🎯 Recommended configuration:")
            print(f"   LMSTUDIO_API_URL={working_url}")
            print(f"   DEFAULT_LMSTUDIO_MODEL={working_model}")
        
    else:
        print("\n❌ Could not connect to LM Studio")
        print("Please ensure LM Studio is running with a loaded model")
