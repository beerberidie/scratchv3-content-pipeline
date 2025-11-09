#!/usr/bin/env python3
"""
ScratchV3 External Access Setup
Configures SSL certificates, DNS, and provides guidance for router/firewall setup
"""
import os
import subprocess
import sys
import requests
import socket
from pathlib import Path

def get_public_ip():
    """Get the current public IP address"""
    try:
        response = requests.get('https://api.ipify.org', timeout=10)
        return response.text.strip()
    except Exception as e:
        print(f"⚠️  Could not get public IP: {e}")
        return None

def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "192.168.1.4"

def check_mkcert_available():
    """Check if mkcert is available"""
    try:
        subprocess.run(["mkcert", "-version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def create_comprehensive_ssl_certificate():
    """Create SSL certificate with both local and external domains"""
    print("🔐 Creating Comprehensive SSL Certificate")
    print("=" * 50)
    
    if not check_mkcert_available():
        print("❌ mkcert not found. Please install mkcert first.")
        return False
    
    # Define all domains and IPs
    domains = [
        "localhost",
        "127.0.0.1",
        "192.168.1.4",
        "*.localhost",
        "localhost.localdomain",
        "scratchgpt.webhop.me",  # No-IP domain
        "*.scratchgpt.webhop.me"  # Wildcard for subdomains
    ]
    
    print("📋 Certificate will include:")
    for domain in domains:
        print(f"   • {domain}")
    
    # Create certificate
    cmd = ["mkcert"] + domains
    
    try:
        print("\n🔨 Generating certificate...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Find generated files
        cert_files = []
        for file in os.listdir("."):
            if file.endswith(".pem") and ("localhost" in file or "scratchgpt" in file):
                cert_files.append(file)
        
        if len(cert_files) >= 2:
            cert_file = None
            key_file = None
            
            for file in cert_files:
                if "key" in file:
                    key_file = file
                else:
                    cert_file = file
            
            if cert_file and key_file:
                print(f"✅ Certificate created successfully!")
                print(f"   Certificate: {cert_file}")
                print(f"   Private Key: {key_file}")
                return cert_file, key_file
        
        print("❌ Could not identify certificate files")
        return None, None
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating certificate: {e}")
        return None, None

def update_env_configuration(cert_file, key_file):
    """Update .env file with new certificate"""
    print("\n⚙️  Updating .env Configuration")
    print("=" * 40)
    
    env_file = ".env"
    if not os.path.exists(env_file):
        print("❌ .env file not found")
        return False
    
    # Read current .env
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update SSL configuration
    updated_lines = []
    for line in lines:
        if line.startswith("SSL_CERTFILE="):
            updated_lines.append(f"SSL_CERTFILE=./{cert_file}\n")
        elif line.startswith("SSL_KEYFILE="):
            updated_lines.append(f"SSL_KEYFILE=./{key_file}\n")
        else:
            updated_lines.append(line)
    
    # Write updated .env
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print("✅ .env file updated with new certificate")
    return True

def check_no_ip_dns():
    """Check No-IP DNS resolution"""
    print("\n🌐 Checking No-IP DNS Resolution")
    print("=" * 40)
    
    domain = "scratchgpt.webhop.me"
    
    try:
        resolved_ip = socket.gethostbyname(domain)
        public_ip = get_public_ip()
        
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

def provide_router_configuration():
    """Provide router port forwarding instructions"""
    print("\n🌐 Router Port Forwarding Configuration")
    print("=" * 50)
    
    local_ip = get_local_ip()
    
    print("📋 Port Forwarding Settings:")
    print(f"   External Port: 8442")
    print(f"   Internal IP: {local_ip}")
    print(f"   Internal Port: 8081")
    print(f"   Protocol: TCP")
    print(f"   Description: ScratchV3 HTTPS")
    
    print("\n🔧 Router Configuration Steps:")
    print("1. Access your router's admin panel (usually 192.168.1.1 or 192.168.0.1)")
    print("2. Look for 'Port Forwarding', 'Virtual Server', or 'NAT' settings")
    print("3. Create a new rule with the settings above")
    print("4. Save and restart your router if required")
    
    print("\n📱 Common Router Interfaces:")
    print("   • Linksys: Advanced → Security → Apps and Gaming → Single Port Forwarding")
    print("   • Netgear: Dynamic DNS → Port Forwarding / Port Triggering")
    print("   • TP-Link: Advanced → NAT Forwarding → Port Forwarding")
    print("   • ASUS: Adaptive QoS → Traditional QoS → Port Forwarding")

def provide_firewall_configuration():
    """Provide Windows Firewall configuration"""
    print("\n🛡️  Windows Firewall Configuration")
    print("=" * 50)
    
    print("🔧 Manual Configuration:")
    print("1. Open Windows Defender Firewall with Advanced Security")
    print("2. Click 'Inbound Rules' → 'New Rule'")
    print("3. Select 'Port' → 'TCP' → Specific port: 8081")
    print("4. Allow the connection")
    print("5. Apply to all profiles (Domain, Private, Public)")
    print("6. Name: 'ScratchV3 External Access'")
    
    print("\n⚡ PowerShell Command (Run as Administrator):")
    print("New-NetFirewallRule -DisplayName 'ScratchV3-External' -Direction Inbound -Protocol TCP -LocalPort 8081 -Action Allow -Profile Any")

def provide_no_ip_configuration():
    """Provide No-IP configuration instructions"""
    print("\n🌍 No-IP Dynamic DNS Configuration")
    print("=" * 50)
    
    public_ip = get_public_ip()
    
    print("📋 No-IP Settings:")
    print(f"   Hostname: scratchgpt.webhop.me")
    print(f"   IP Address: {public_ip if public_ip else 'YOUR_PUBLIC_IP'}")
    print(f"   Record Type: A (Host)")
    
    print("\n🔧 Configuration Steps:")
    print("1. Log in to your No-IP account at https://www.noip.com")
    print("2. Go to 'Dynamic DNS' → 'No-IP Hostnames'")
    print("3. Find 'scratchgpt.webhop.me' and click 'Modify'")
    print(f"4. Update IP address to: {public_ip if public_ip else 'YOUR_CURRENT_PUBLIC_IP'}")
    print("5. Save changes")
    
    print("\n🔄 Automatic Updates:")
    print("• Install No-IP DUC (Dynamic Update Client) for automatic IP updates")
    print("• Download from: https://www.noip.com/download")
    print("• Configure with your No-IP credentials")

def test_local_access():
    """Test local access to verify application is running"""
    print("\n🧪 Testing Local Access")
    print("=" * 30)
    
    endpoints = [
        "https://localhost:8081/health",
        "https://192.168.1.4:8081/health"
    ]
    
    for endpoint in endpoints:
        try:
            import urllib3
            urllib3.disable_warnings()
            response = requests.get(endpoint, timeout=5, verify=False)
            if response.status_code == 200:
                print(f"✅ {endpoint}")
            else:
                print(f"⚠️  {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def provide_testing_instructions():
    """Provide testing instructions"""
    print("\n🧪 Testing External Access")
    print("=" * 40)
    
    print("📱 Test from external network (mobile data, different location):")
    print("   • https://scratchgpt.webhop.me:8442")
    print("   • Should show ScratchV3 login page")
    print("   • SSL certificate should be trusted")
    
    print("\n🔍 Online Testing Tools:")
    print("   • Port Checker: https://www.yougetsignal.com/tools/open-ports/")
    print("   • DNS Checker: https://dnschecker.org/")
    print("   • SSL Checker: https://www.sslshopper.com/ssl-checker.html")
    
    print("\n⚠️  Troubleshooting:")
    print("   • If connection refused: Check router port forwarding")
    print("   • If DNS not resolving: Update No-IP configuration")
    print("   • If SSL errors: Restart application with new certificate")

def main():
    """Main setup function"""
    print("🌍 ScratchV3 External Access Setup")
    print("=" * 50)
    
    # Get network information
    public_ip = get_public_ip()
    local_ip = get_local_ip()
    
    print(f"🌐 Network Information:")
    print(f"   Public IP: {public_ip if public_ip else 'Unable to detect'}")
    print(f"   Local IP: {local_ip}")
    print(f"   Target Domain: scratchgpt.webhop.me")
    print(f"   External URL: https://scratchgpt.webhop.me:8442")
    
    # Create comprehensive SSL certificate
    cert_result = create_comprehensive_ssl_certificate()
    if cert_result and cert_result[0] and cert_result[1]:
        cert_file, key_file = cert_result
        update_env_configuration(cert_file, key_file)
    else:
        print("⚠️  SSL certificate creation failed. Using existing certificate.")
    
    # Check DNS resolution
    check_no_ip_dns()
    
    # Test local access
    test_local_access()
    
    # Provide configuration instructions
    provide_router_configuration()
    provide_firewall_configuration()
    provide_no_ip_configuration()
    provide_testing_instructions()
    
    print("\n" + "=" * 50)
    print("📋 SETUP CHECKLIST")
    print("=" * 50)
    print("□ 1. SSL certificate updated with No-IP domain")
    print("□ 2. Router port forwarding: 8442 → 192.168.1.4:8081")
    print("□ 3. Windows Firewall rule for port 8081")
    print("□ 4. No-IP DNS pointing to your public IP")
    print("□ 5. Application restarted with new certificate")
    print("□ 6. External access tested from different network")
    
    print("\n🚀 After completing the checklist:")
    print("   Restart ScratchV3: python run.py")
    print("   Test: https://scratchgpt.webhop.me:8442")

if __name__ == "__main__":
    main()
