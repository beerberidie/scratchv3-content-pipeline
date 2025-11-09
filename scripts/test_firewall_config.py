#!/usr/bin/env python3
"""
Firewall Configuration Test Script
"""
import socket
import subprocess

def test_local_port():
    """Test if port 8081 is accessible locally"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 8081))
        sock.close()
        if result == 0:
            print("✅ Port 8081 is accessible locally")
            return True
        else:
            print("❌ Port 8081 is not accessible locally")
            return False
    except Exception as e:
        print(f"❌ Local port test failed: {e}")
        return False

def check_firewall_rules():
    """Check if firewall rules exist"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", 'Get-NetFirewallRule -DisplayName "*ScratchV3*"'],
            capture_output=True, text=True
        )
        if "ScratchV3" in result.stdout:
            print("✅ ScratchV3 firewall rules exist")
            return True
        else:
            print("❌ ScratchV3 firewall rules not found")
            return False
    except Exception as e:
        print(f"❌ Firewall rule check failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Firewall Configuration Test")
    print("=" * 30)
    test_local_port()
    check_firewall_rules()
