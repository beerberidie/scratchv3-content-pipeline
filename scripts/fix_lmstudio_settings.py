#!/usr/bin/env python3
"""
Script to fix LM Studio settings by making API calls to your running app
"""
import asyncio
import httpx
import json

async def fix_lmstudio_settings():
    """Fix LM Studio settings via API"""
    
    base_url = "https://localhost:8081"
    
    print("🔧 Fixing LM Studio Settings")
    print("=" * 40)
    
    # Create HTTP client that ignores SSL verification for localhost
    async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
        
        # Step 1: Get current settings
        print("📋 Step 1: Getting current settings...")
        try:
            response = await client.get(f"{base_url}/api/settings/")
            if response.status_code == 200:
                current_settings = response.json()
                print(f"✅ Current AI Provider: {current_settings.get('ai_provider', 'Unknown')}")
                print(f"✅ Current LM Studio URL: {current_settings.get('lmstudio_api_url', 'Not set')}")
                print(f"✅ Current LM Studio Model: {current_settings.get('lmstudio_model', 'Not set')}")
            else:
                print(f"❌ Failed to get settings: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ Error getting settings: {e}")
            return
        
        # Step 2: Update settings to use LM Studio
        print("\n🔄 Step 2: Updating settings to use LM Studio...")
        
        new_settings = {
            "ai_provider": "lmstudio",
            "openai_api_key": current_settings.get("openai_api_key"),
            "openai_model": current_settings.get("openai_model", "gpt-4"),
            "openrouter_api_key": current_settings.get("openrouter_api_key"),
            "openrouter_model": current_settings.get("openrouter_model", "openrouter/auto"),
            "lmstudio_api_url": "http://127.0.0.1:1234/v1",
            "lmstudio_model": "qwen3-4b",
            "pexels_api_key": current_settings.get("pexels_api_key"),
            "wordpress_url_presets": current_settings.get("wordpress_url_presets", []),
            "wordpress_app_username": current_settings.get("wordpress_app_username"),
            "wordpress_app_password": current_settings.get("wordpress_app_password")
        }
        
        try:
            response = await client.post(
                f"{base_url}/api/settings/",
                json=new_settings,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("✅ Settings updated successfully!")
            else:
                print(f"❌ Failed to update settings: {response.status_code}")
                print(f"Response: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error updating settings: {e}")
            return
        
        # Step 3: Test the LM Studio connection
        print("\n🧪 Step 3: Testing LM Studio connection...")
        
        test_payload = {
            "provider": "lmstudio",
            "api_key": "http://127.0.0.1:1234/v1"  # For LM Studio, this is the URL
        }
        
        try:
            response = await client.post(
                f"{base_url}/api/keys/test",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("valid"):
                    print("✅ LM Studio connection test successful!")
                    print(f"Message: {result.get('message', 'Connection verified')}")
                else:
                    print(f"❌ LM Studio connection test failed: {result.get('message', 'Unknown error')}")
            else:
                print(f"❌ Connection test request failed: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Error testing connection: {e}")
        
        # Step 4: Verify final settings
        print("\n✅ Step 4: Verifying final settings...")
        try:
            response = await client.get(f"{base_url}/api/settings/")
            if response.status_code == 200:
                final_settings = response.json()
                print(f"✅ Final AI Provider: {final_settings.get('ai_provider')}")
                print(f"✅ Final LM Studio URL: {final_settings.get('lmstudio_api_url')}")
                print(f"✅ Final LM Studio Model: {final_settings.get('lmstudio_model')}")
                
                if (final_settings.get('ai_provider') == 'lmstudio' and 
                    final_settings.get('lmstudio_api_url') == 'http://127.0.0.1:1234/v1' and
                    final_settings.get('lmstudio_model') == 'qwen3-4b'):
                    print("\n🎉 SUCCESS! LM Studio is now properly configured!")
                    print("\nNext steps:")
                    print("1. Try creating a new task in your dashboard")
                    print("2. The 404 errors should be resolved")
                else:
                    print("\n⚠️  Settings may not have been applied correctly")
            else:
                print(f"❌ Failed to verify settings: {response.status_code}")
        except Exception as e:
            print(f"❌ Error verifying settings: {e}")

if __name__ == "__main__":
    asyncio.run(fix_lmstudio_settings())
