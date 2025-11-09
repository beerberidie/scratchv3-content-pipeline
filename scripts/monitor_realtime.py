#!/usr/bin/env python3
"""
Real-time DNS and IP Monitoring for ScratchV3
Monitors for changes in public IP and DNS resolution
"""
import requests
import socket
import time
from datetime import datetime

def monitor_changes():
    """Monitor IP and DNS changes"""
    print("🔍 Starting Real-time Monitoring")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    last_public_ip = None
    last_dns_ip = None
    
    while True:
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Get current public IP
            try:
                public_ip = requests.get('https://api.ipify.org', timeout=5).text.strip()
            except:
                public_ip = "Error"
            
            # Get DNS resolution
            try:
                dns_ip = socket.gethostbyname('scratchgpt.webhop.me')
            except:
                dns_ip = "No resolution"
            
            # Check for changes
            ip_changed = last_public_ip and last_public_ip != public_ip
            dns_changed = last_dns_ip and last_dns_ip != dns_ip
            
            status = "✅ OK" if public_ip == dns_ip else "❌ MISMATCH"
            
            print(f"[{current_time}] Public: {public_ip} | DNS: {dns_ip} | {status}")
            
            if ip_changed:
                print(f"  🚨 PUBLIC IP CHANGED: {last_public_ip} → {public_ip}")
            
            if dns_changed:
                print(f"  🚨 DNS IP CHANGED: {last_dns_ip} → {dns_ip}")
            
            last_public_ip = public_ip
            last_dns_ip = dns_ip
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"  ❌ Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    monitor_changes()
