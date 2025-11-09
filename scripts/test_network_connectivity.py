#!/usr/bin/env python3
"""
Network Connectivity Test for ScratchV3 Application
Tests firewall settings, port accessibility, and network configuration
"""
import socket
import subprocess
import sys
import time
import requests
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(InsecureRequestWarning)

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "192.168.1.4"  # Fallback

def test_port_accessibility(host, port):
    """Test if a port is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def test_dns_resolution():
    """Test DNS resolution for localhost"""
    print("🔍 Testing DNS Resolution")
    print("=" * 30)
    
    hosts_to_test = [
        ("localhost", "127.0.0.1"),
        ("127.0.0.1", "127.0.0.1"),
    ]
    
    for hostname, expected_ip in hosts_to_test:
        try:
            resolved_ip = socket.gethostbyname(hostname)
            status = "✅" if resolved_ip == expected_ip else "⚠️"
            print(f"{status} {hostname} → {resolved_ip}")
        except Exception as e:
            print(f"❌ {hostname} → Error: {e}")

def test_firewall_and_ports():
    """Test firewall and port accessibility"""
    print("\n🛡️  Testing Firewall and Ports")
    print("=" * 40)
    
    local_ip = get_local_ip()
    port = 8081
    
    hosts_to_test = [
        ("localhost", "127.0.0.1"),
        ("127.0.0.1", "127.0.0.1"),
        ("Local IP", local_ip),
    ]
    
    print(f"Testing port {port} accessibility:")
    
    for name, host in hosts_to_test:
        accessible = test_port_accessibility(host, port)
        status = "✅" if accessible else "❌"
        print(f"{status} {name} ({host}):{port}")
        
        if not accessible and host == local_ip:
            print("   ⚠️  Local IP not accessible - check Windows Firewall")

def test_https_endpoints():
    """Test HTTPS endpoints"""
    print("\n🔐 Testing HTTPS Endpoints")
    print("=" * 35)
    
    local_ip = get_local_ip()
    endpoints = [
        f"https://localhost:8081/health",
        f"https://127.0.0.1:8081/health",
        f"https://{local_ip}:8081/health"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"Testing: {endpoint}")
            response = requests.get(endpoint, timeout=10, verify=False)
            if response.status_code == 200:
                print(f"✅ {endpoint} - Status: {response.status_code}")
            else:
                print(f"⚠️  {endpoint} - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} - Connection refused")
        except requests.exceptions.Timeout:
            print(f"❌ {endpoint} - Timeout")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def check_windows_firewall():
    """Check Windows Firewall status"""
    print("\n🛡️  Windows Firewall Status")
    print("=" * 35)
    
    try:
        # Check firewall status
        result = subprocess.run(
            ["netsh", "advfirewall", "show", "allprofiles", "state"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if "State" in line:
                    print(f"🔥 {line.strip()}")
        else:
            print("❌ Could not check firewall status")
            
    except Exception as e:
        print(f"❌ Error checking firewall: {e}")

def check_listening_ports():
    """Check what's listening on port 8081"""
    print("\n👂 Checking Listening Ports")
    print("=" * 35)
    
    try:
        result = subprocess.run(
            ["netstat", "-an", "|", "findstr", ":8081"],
            shell=True, capture_output=True, text=True
        )
        
        if result.stdout.strip():
            print("🔍 Port 8081 status:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"   {line.strip()}")
        else:
            print("❌ No process listening on port 8081")
            print("   Make sure your ScratchV3 app is running!")
            
    except Exception as e:
        print(f"❌ Error checking ports: {e}")

def provide_firewall_fix():
    """Provide firewall fix instructions"""
    print("\n🔧 Firewall Fix Instructions")
    print("=" * 40)
    
    print("If 192.168.1.4:8081 is not accessible:")
    print("\n1️⃣  Quick Fix - Allow Python:")
    print("   • Press Win+R, type: wf.msc")
    print("   • Click 'Inbound Rules' → 'New Rule'")
    print("   • Select 'Program' → Browse to python.exe")
    print("   • Allow the connection")
    print("   • Apply to all profiles")
    
    print("\n2️⃣  Alternative - Allow Port 8081:")
    print("   • Press Win+R, type: wf.msc")
    print("   • Click 'Inbound Rules' → 'New Rule'")
    print("   • Select 'Port' → TCP → 8081")
    print("   • Allow the connection")
    print("   • Apply to all profiles")
    
    print("\n3️⃣  PowerShell Command (Run as Admin):")
    print("   New-NetFirewallRule -DisplayName 'ScratchV3' -Direction Inbound -Protocol TCP -LocalPort 8081 -Action Allow")

def run_connectivity_tests():
    """Run all connectivity tests"""
    print("🌐 ScratchV3 Network Connectivity Test")
    print("=" * 50)
    
    # Test DNS resolution
    test_dns_resolution()
    
    # Test firewall and ports
    test_firewall_and_ports()
    
    # Check Windows Firewall
    check_windows_firewall()
    
    # Check listening ports
    check_listening_ports()
    
    # Test HTTPS endpoints (if app is running)
    print("\n⚠️  Make sure ScratchV3 is running before HTTPS tests!")
    try:
        choice = input("Is ScratchV3 running? Test HTTPS endpoints? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            test_https_endpoints()
    except KeyboardInterrupt:
        print("\nSkipping HTTPS tests...")
    
    # Provide firewall fix instructions
    provide_firewall_fix()

def main():
    """Main function"""
    run_connectivity_tests()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY & NEXT STEPS")
    print("=" * 50)
    print("1. ✅ If all localhost/127.0.0.1 tests pass:")
    print("   → Your SSL setup is working correctly!")
    
    print("\n2. ❌ If 192.168.1.4 tests fail:")
    print("   → Configure Windows Firewall (see instructions above)")
    
    print("\n3. 🚀 Final Test Steps:")
    print("   • Restart ScratchV3 application")
    print("   • Clear browser cache")
    print("   • Test: https://localhost:8081")
    print("   • Test: https://127.0.0.1:8081")
    print("   • Test: https://192.168.1.4:8081 (after firewall fix)")
    
    print("\n4. 🆘 If still having issues:")
    print("   • Try incognito/private browsing")
    print("   • Restart browser completely")
    print("   • Check antivirus software")
    print("   • Verify certificate trust (run browser_trust_setup.py)")

if __name__ == "__main__":
    main()
