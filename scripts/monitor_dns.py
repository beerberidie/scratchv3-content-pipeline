#!/usr/bin/env python3
"""
DNS Monitoring Script for No-IP
Monitors DNS resolution and alerts if IP changes
"""
import socket
import requests
import time
from datetime import datetime

def get_public_ip():
    """Get current public IP"""
    try:
        return requests.get('https://api.ipify.org', timeout=10).text.strip()
    except:
        return None

def check_dns_resolution():
    """Check DNS resolution"""
    try:
        return socket.gethostbyname('scratchgpt.webhop.me')
    except:
        return None

def monitor_dns():
    """Monitor DNS resolution"""
    print("🔍 DNS Monitoring Started")
    print("=" * 30)
    
    while True:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        public_ip = get_public_ip()
        resolved_ip = check_dns_resolution()
        
        print(f"[{current_time}]")
        print(f"  Public IP: {public_ip}")
        print(f"  DNS IP: {resolved_ip}")
        
        if public_ip and resolved_ip:
            if public_ip == resolved_ip:
                print("  Status: ✅ OK")
            else:
                print("  Status: ⚠️  MISMATCH - Update needed!")
        else:
            print("  Status: ❌ ERROR")
        
        print("-" * 30)
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    monitor_dns()
