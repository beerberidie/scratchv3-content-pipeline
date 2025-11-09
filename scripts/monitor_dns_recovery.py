#!/usr/bin/env python3
"""
DNS Recovery Monitor for scratchgpt.webhop.me
Monitors DNS resolution recovery after No-IP update
"""
import socket
import time
from datetime import datetime

def monitor_dns_recovery():
    """Monitor DNS recovery"""
    domain = "scratchgpt.webhop.me"
    print(f"🔍 Monitoring DNS recovery for {domain}")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    consecutive_successes = 0
    
    while True:
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            
            try:
                resolved_ip = socket.gethostbyname(domain)
                consecutive_successes += 1
                print(f"[{current_time}] ✅ {domain} → {resolved_ip} (Success #{consecutive_successes})")
                
                if consecutive_successes >= 3:
                    print(f"\n🎉 DNS RECOVERY CONFIRMED!")
                    print(f"   {domain} is now resolving consistently")
                    print(f"   You can now test: https://{domain}:8442")
                    break
                    
            except socket.gaierror:
                consecutive_successes = 0
                print(f"[{current_time}] ❌ {domain} - Still not resolving")
            
            time.sleep(60)  # Check every minute
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            break

if __name__ == "__main__":
    monitor_dns_recovery()
