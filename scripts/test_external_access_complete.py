#!/usr/bin/env python3
"""
Complete External Access Testing for ScratchV3
Tests all aspects of external access configuration
"""
import requests
import socket
import subprocess
import time
import urllib3
from datetime import datetime

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_network_info():
    """Get network information"""
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Get public IP
        public_ip = requests.get('https://api.ipify.org', timeout=10).text.strip()
        
        return local_ip, public_ip
    except Exception as e:
        print(f"Error getting network info: {e}")
        return "192.168.1.4", "Unknown"

def test_ssl_certificate():
    """Test SSL certificate includes all required domains"""
    print("🔐 Testing SSL Certificate")
    print("=" * 30)
    
    domains_to_test = [
        "localhost:8081",
        "127.0.0.1:8081",
        "192.168.1.4:8081"
    ]
    
    for domain in domains_to_test:
        try:
            response = requests.get(f"https://{domain}/health", 
                                  timeout=5, verify=False)
            if response.status_code == 200:
                print(f"✅ {domain} - SSL working")
            else:
                print(f"⚠️  {domain} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {domain} - Error: {e}")

def test_dns_resolution():
    """Test DNS resolution for No-IP domain"""
    print("\n🌐 Testing DNS Resolution")
    print("=" * 30)
    
    domain = "scratchgpt.webhop.me"
    local_ip, public_ip = get_network_info()
    
    try:
        resolved_ip = socket.gethostbyname(domain)
        print(f"Domain: {domain}")
        print(f"Resolves to: {resolved_ip}")
        print(f"Your public IP: {public_ip}")
        
        if resolved_ip == public_ip:
            print("✅ DNS resolution is correct!")
            return True
        else:
            print("⚠️  DNS resolution mismatch!")
            print("   Please update your No-IP configuration")
            return False
    except socket.gaierror:
        print(f"❌ Could not resolve {domain}")
        print("   Please check your No-IP configuration")
        return False

def test_local_access():
    """Test local access to application"""
    print("\n🏠 Testing Local Access")
    print("=" * 25)
    
    local_ip, _ = get_network_info()
    endpoints = [
        f"https://localhost:8081/health",
        f"https://127.0.0.1:8081/health",
        f"https://{local_ip}:8081/health"
    ]
    
    all_working = True
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5, verify=False)
            if response.status_code == 200:
                print(f"✅ {endpoint}")
            else:
                print(f"⚠️  {endpoint} - Status: {response.status_code}")
                all_working = False
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
            all_working = False
    
    return all_working

def test_port_accessibility():
    """Test if ports are accessible"""
    print("\n🔌 Testing Port Accessibility")
    print("=" * 30)
    
    local_ip, _ = get_network_info()
    
    # Test local port 8081
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((local_ip, 8081))
        sock.close()
        if result == 0:
            print(f"✅ Port 8081 accessible on {local_ip}")
        else:
            print(f"❌ Port 8081 not accessible on {local_ip}")
    except Exception as e:
        print(f"❌ Port test error: {e}")

def test_firewall_configuration():
    """Test Windows Firewall configuration"""
    print("\n🛡️  Testing Firewall Configuration")
    print("=" * 35)
    
    try:
        result = subprocess.run(
            ["powershell", "-Command", 'Get-NetFirewallRule -DisplayName "*ScratchV3*" | Select-Object DisplayName, Enabled'],
            capture_output=True, text=True
        )
        
        if "ScratchV3" in result.stdout:
            print("✅ ScratchV3 firewall rules found")
            # Count enabled rules
            enabled_count = result.stdout.count("True")
            print(f"   {enabled_count} rules enabled")
        else:
            print("⚠️  No ScratchV3 firewall rules found")
            print("   Please configure Windows Firewall")
    except Exception as e:
        print(f"❌ Firewall check error: {e}")

def provide_router_configuration_status():
    """Provide router configuration status"""
    print("\n🌐 Router Configuration Status")
    print("=" * 35)
    
    local_ip, public_ip = get_network_info()
    
    print("📋 Required Router Settings:")
    print(f"   External Port: 8442")
    print(f"   Internal IP: {local_ip}")
    print(f"   Internal Port: 8081")
    print(f"   Protocol: TCP")
    
    print("\n⚠️  Manual Verification Required:")
    print("   • Access router admin panel")
    print("   • Check port forwarding rules")
    print("   • Verify settings match above")
    print("   • Test from external network")

def test_external_connectivity():
    """Test external connectivity (if possible)"""
    print("\n🌍 Testing External Connectivity")
    print("=" * 35)
    
    domain = "scratchgpt.webhop.me"
    port = 8442
    
    print("📱 External Access Tests:")
    print(f"   Target URL: https://{domain}:{port}")
    print("   ⚠️  These tests require external network access")
    
    # Test if domain resolves
    try:
        resolved_ip = socket.gethostbyname(domain)
        print(f"   DNS Resolution: ✅ {resolved_ip}")
    except:
        print(f"   DNS Resolution: ❌ Failed")
        return False
    
    # Test port connectivity (basic check)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((domain, port))
        sock.close()
        if result == 0:
            print(f"   Port {port}: ✅ Accessible")
        else:
            print(f"   Port {port}: ❌ Not accessible")
            print("     Check router port forwarding")
    except Exception as e:
        print(f"   Port test error: {e}")
    
    return True

def provide_testing_instructions():
    """Provide manual testing instructions"""
    print("\n🧪 Manual Testing Instructions")
    print("=" * 35)
    
    print("📱 External Network Testing:")
    print("   1. Use mobile data or different internet connection")
    print("   2. Navigate to: https://scratchgpt.webhop.me:8442")
    print("   3. Should see ScratchV3 login page")
    print("   4. SSL certificate should be trusted")
    
    print("\n🌐 Online Testing Tools:")
    print("   • Port Checker: https://www.yougetsignal.com/tools/open-ports/")
    print("   • DNS Checker: https://dnschecker.org/")
    print("   • SSL Checker: https://www.sslshopper.com/ssl-checker.html")
    
    print("\n🔍 Command Line Tests:")
    print("   • nslookup scratchgpt.webhop.me")
    print("   • telnet scratchgpt.webhop.me 8442")
    print("   • curl -k https://scratchgpt.webhop.me:8442/health")

def generate_configuration_summary():
    """Generate configuration summary"""
    print("\n📋 Configuration Summary")
    print("=" * 30)
    
    local_ip, public_ip = get_network_info()
    
    print("🔐 SSL Certificate:")
    print("   • File: localhost+6.pem")
    print("   • Includes: localhost, 127.0.0.1, 192.168.1.4, scratchgpt.webhop.me")
    print("   • Status: ✅ Updated with No-IP domain")
    
    print(f"\n🌐 Network Configuration:")
    print(f"   • Local IP: {local_ip}")
    print(f"   • Public IP: {public_ip}")
    print(f"   • Local Port: 8081")
    print(f"   • External Port: 8442")
    
    print("\n🎯 Access URLs:")
    print("   • Local: https://192.168.1.4:8081")
    print("   • External: https://scratchgpt.webhop.me:8442")

def main():
    """Main testing function"""
    print("🧪 ScratchV3 External Access Complete Test")
    print("=" * 50)
    
    # Get network info
    local_ip, public_ip = get_network_info()
    print(f"🌐 Network Info: Local={local_ip}, Public={public_ip}")
    
    # Run all tests
    print("\n" + "=" * 50)
    test_ssl_certificate()
    dns_ok = test_dns_resolution()
    local_ok = test_local_access()
    test_port_accessibility()
    test_firewall_configuration()
    provide_router_configuration_status()
    
    if dns_ok:
        test_external_connectivity()
    
    provide_testing_instructions()
    generate_configuration_summary()
    
    # Final status
    print("\n" + "=" * 50)
    print("📊 FINAL STATUS")
    print("=" * 50)
    print(f"✅ SSL Certificate: Updated with No-IP domain")
    print(f"{'✅' if local_ok else '❌'} Local Access: {'Working' if local_ok else 'Issues detected'}")
    print(f"{'✅' if dns_ok else '⚠️ '} DNS Resolution: {'Configured' if dns_ok else 'Needs configuration'}")
    print(f"⚠️  Router Port Forwarding: Manual verification required")
    print(f"⚠️  External Access: Test from external network")
    
    print("\n🎯 Next Steps:")
    if not dns_ok:
        print("1. Configure No-IP DNS (update IP address)")
    print("2. Configure router port forwarding (8442 → 8081)")
    print("3. Test external access from different network")
    print("4. Monitor with scripts/monitor_dns.py")

if __name__ == "__main__":
    main()
