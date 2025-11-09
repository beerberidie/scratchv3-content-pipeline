#!/usr/bin/env python3
"""
Check current user settings via API
"""
import requests
import json
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost:8081"

def check_settings():
    """Check current settings for all users"""
    
    print("🔍 Checking Current User Settings...")
    
    # Read the users.json file directly
    try:
        with open('data/users.json', 'r') as f:
            users_data = json.load(f)
        
        print("\n📊 Current Settings in Database:")
        print("=" * 50)
        
        for username, user_data in users_data.items():
            settings = user_data.get('settings', {})
            ai_provider = settings.get('ai_provider', 'NOT SET')
            lmstudio_url = settings.get('lmstudio_api_url', 'NOT SET')
            lmstudio_model = settings.get('lmstudio_model', 'NOT SET')
            
            print(f"\n👤 User: {username}")
            print(f"   AI Provider: {ai_provider}")
            if ai_provider == 'lmstudio':
                print(f"   LM Studio URL: {lmstudio_url}")
                print(f"   LM Studio Model: {lmstudio_model}")
                print("   ✅ Using LM Studio!")
            else:
                print("   ❌ Not using LM Studio")
        
        print("\n" + "=" * 50)
        
        # Check if any user has LM Studio settings
        lmstudio_users = [username for username, user_data in users_data.items() 
                         if user_data.get('settings', {}).get('ai_provider') == 'lmstudio']
        
        if lmstudio_users:
            print(f"✅ Users with LM Studio: {', '.join(lmstudio_users)}")
        else:
            print("❌ No users are currently using LM Studio")
            print("💡 This means your recent save might not have worked, or you haven't saved LM Studio settings yet.")
        
    except FileNotFoundError:
        print("❌ Could not find users.json file")
    except json.JSONDecodeError:
        print("❌ Could not parse users.json file")
    except Exception as e:
        print(f"❌ Error reading settings: {e}")

if __name__ == "__main__":
    check_settings()
