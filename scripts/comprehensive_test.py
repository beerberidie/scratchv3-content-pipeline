#!/usr/bin/env python3
"""
Comprehensive External Access Test
Tests all aspects of external connectivity
"""
import subprocess
import requests
import socket
import time
from datetime import datetime

def comprehensive_test():
    """Run comprehensive connectivity test"""
    print("🧪 Comprehensive External Access Test")
    print("=" * 45)
    
    # Test 1: Local application
    print("\n1️⃣  Testing Local Application:")
    try:
        response = requests.get('https://192.168.1.4:8081/health', verify=False, timeout=5)
        print(f"   ✅ Local app: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Local app: {e}")
        return
    
    # Test 2: DNS resolution
    print("\n2️⃣  Testing DNS Resolution:")
    try:
        ip = socket.gethostbyname('scratchgpt.webhop.me')
        print(f"   ✅ DNS resolves to: {ip}")
        dns_working = True
    except:
        print(f"   ❌ DNS resolution failed")
        dns_working = False
    
    # Test 3: Direct IP access
    print("\n3️⃣  Testing Direct IP Access:")
    try:
        response = requests.get('https://197.92.227.126:8442/health', verify=False, timeout=10)
        print(f"   ✅ Direct IP: Status {response.status_code}")
        direct_working = True
    except Exception as e:
        print(f"   ❌ Direct IP: {e}")
        direct_working = False
    
    # Test 4: Domain access (if DNS working)
    if dns_working:
        print("\n4️⃣  Testing Domain Access:")
        try:
            response = requests.get('https://scratchgpt.webhop.me:8442/health', verify=False, timeout=10)
            print(f"   ✅ Domain access: Status {response.status_code}")
            print("   🎉 EXTERNAL ACCESS WORKING!")
        except Exception as e:
            print(f"   ❌ Domain access: {e}")
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"   Local App: {'✅' if True else '❌'}")
    print(f"   DNS Resolution: {'✅' if dns_working else '❌'}")
    print(f"   Direct IP Access: {'✅' if direct_working else '❌'}")
    
    if dns_working and direct_working:
        print("\n🎯 Result: External access should be working!")
        print("   Try: https://scratchgpt.webhop.me:8442")
    elif direct_working and not dns_working:
        print("\n🎯 Result: Router/app working, DNS propagation needed")
        print("   Wait for DNS propagation or use direct IP")
    else:
        print("\n🎯 Result: Check router port forwarding")

if __name__ == "__main__":
    comprehensive_test()
