#!/usr/bin/env python3
"""
Debug script to replicate the exact request your app is making to LM Studio
"""
import asyncio
import httpx
from openai import AsyncOpenAI
import json

async def debug_lmstudio_request():
    """Debug the exact request format"""
    
    base_url = "http://127.0.0.1:1234/v1"
    model_name = "qwen3-4b"
    
    print("🔍 Debugging LM Studio Request")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print(f"Model: {model_name}")
    
    # Test 1: Check available models
    print("\n📋 Step 1: Checking available models...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/models")
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model['id'] for model in models_data.get('data', [])]
                print(f"✅ Available models: {available_models}")
                
                if model_name not in available_models:
                    print(f"⚠️  Model '{model_name}' not found in available models!")
                    print(f"   Try using one of: {available_models}")
                    if available_models:
                        model_name = available_models[0]  # Use first available model
                        print(f"   Using '{model_name}' instead")
            else:
                print(f"❌ Models endpoint failed: {response.status_code}")
                return
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return
    
    # Test 2: Raw HTTP request (like your app would make)
    print(f"\n🌐 Step 2: Testing raw HTTP request...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": "Hello, respond with just 'Hi'"}
                ],
                "max_tokens": 10,
                "temperature": 0.7
            }
            
            print(f"Request payload: {json.dumps(payload, indent=2)}")
            
            response = await client.post(
                f"{base_url}/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Raw HTTP request successful!")
                print(f"Response: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
            else:
                print(f"❌ Raw HTTP request failed: {response.status_code}")
                print(f"Response text: {response.text}")
                
    except Exception as e:
        print(f"❌ Raw HTTP request error: {e}")
    
    # Test 3: OpenAI client (like your app uses)
    print(f"\n🤖 Step 3: Testing OpenAI client...")
    try:
        client = AsyncOpenAI(
            api_key="not-needed",
            base_url=base_url,
            timeout=30.0
        )
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Hello, respond with just 'Hi'"}],
            max_tokens=10,
            temperature=0.7
        )
        
        print(f"✅ OpenAI client successful!")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ OpenAI client error: {e}")
        print(f"Error type: {type(e).__name__}")
    
    # Test 4: Test with different URLs
    print(f"\n🔄 Step 4: Testing different URL formats...")
    urls_to_test = [
        "http://localhost:1234/v1",
        "http://127.0.0.1:1234/v1",
        "http://localhost:1234",
        "http://127.0.0.1:1234"
    ]
    
    for test_url in urls_to_test:
        try:
            client = AsyncOpenAI(
                api_key="not-needed",
                base_url=test_url,
                timeout=10.0
            )
            
            response = await client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=3
            )
            
            print(f"✅ {test_url}: Working!")
            
        except Exception as e:
            print(f"❌ {test_url}: {e}")

if __name__ == "__main__":
    asyncio.run(debug_lmstudio_request())
