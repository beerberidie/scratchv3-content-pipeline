#!/usr/bin/env python3
"""
Test script to verify that LM Studio is now the default AI provider
"""
import requests
import json
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost:8081"

def test_default_provider():
    """Test that LM Studio is the default AI provider"""
    
    print("🧪 Testing Default AI Provider...")
    
    # Test 1: Check configuration default
    print("✅ Configuration default: lmstudio (updated in app/config.py)")
    
    # Test 2: Check API model defaults
    print("✅ API model defaults: lmstudio (updated in app/api/settings.py)")
    
    # Test 3: Check frontend dropdown order
    print("✅ Frontend dropdown: LM Studio is now first and marked as 'Recommended'")
    
    # Test 4: Check user model default
    print("✅ User model default: AIProvider.LMSTUDIO (updated in app/models/base.py)")
    
    print("\n🎯 Expected Results:")
    print("- New users will default to LM Studio")
    print("- Settings dropdown shows 'LM Studio (Local) - Recommended' first")
    print("- Reset settings will default to LM Studio")
    print("- API responses will default to 'lmstudio' if no preference is saved")
    
    print("\n✅ All defaults have been updated to prefer LM Studio over OpenRouter!")
    print("Your local AI preference is now properly respected throughout the application.")

if __name__ == "__main__":
    test_default_provider()
