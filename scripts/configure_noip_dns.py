#!/usr/bin/env python3
"""
No-IP Dynamic DNS Configuration Guide
Provides instructions for setting up No-IP DNS to point to your public IP
"""
import requests
import socket
import subprocess
import time

def get_public_ip():
    """Get current public IP address"""
    try:
        response = requests.get('https://api.ipify.org', timeout=10)
        return response.text.strip()
    except Exception as e:
        print(f"⚠️  Could not get public IP: {e}")
        return None

def check_dns_resolution(domain):
    """Check if domain resolves to current public IP"""
    try:
        resolved_ip = socket.gethostbyname(domain)
        return resolved_ip
    except socket.gaierror:
        return None

def test_dns_propagation(domain, expected_ip):
    """Test DNS propagation across different servers"""
    dns_servers = [
        ('Google DNS', '8.8.8.8'),
        ('Cloudflare DNS', '1.1.1.1'),
        ('OpenDNS', '208.67.222.222'),
        ('Quad9 DNS', '9.9.9.9')
    ]
    
    print(f"\n🌐 Testing DNS Propagation for {domain}")
    print("=" * 50)
    
    for name, server in dns_servers:
        try:
            result = subprocess.run(
                ['nslookup', domain, server],
                capture_output=True, text=True, timeout=10
            )
            
            if expected_ip in result.stdout:
                print(f"✅ {name} ({server}): {expected_ip}")
            else:
                print(f"❌ {name} ({server}): Not propagated yet")
                
        except Exception as e:
            print(f"⚠️  {name} ({server}): Error - {e}")

def provide_noip_configuration_steps():
    """Provide No-IP configuration steps"""
    public_ip = get_public_ip()
    domain = "scratchgpt.webhop.me"
    
    print("🌍 No-IP Dynamic DNS Configuration")
    print("=" * 40)
    
    print(f"📋 Configuration Details:")
    print(f"   Domain: {domain}")
    print(f"   Current Public IP: {public_ip if public_ip else 'Unable to detect'}")
    print(f"   Target URL: https://{domain}:8442")
    
    print("\n🔧 Step-by-Step Configuration:")
    print("1️⃣  Access No-IP Account:")
    print("   • Go to: https://www.noip.com")
    print("   • Log in to your account")
    print("   • Navigate to 'Dynamic DNS' → 'No-IP Hostnames'")
    
    print("\n2️⃣  Update Hostname:")
    print(f"   • Find '{domain}' in your hostname list")
    print("   • Click 'Modify' or 'Edit'")
    print(f"   • Update IP Address to: {public_ip if public_ip else '[YOUR_PUBLIC_IP]'}")
    print("   • Ensure Record Type is set to 'A (Host)'")
    print("   • Click 'Update Hostname'")
    
    print("\n3️⃣  Verify Configuration:")
    print("   • Check that the IP address matches your current public IP")
    print("   • Note the TTL (Time To Live) setting")
    print("   • Ensure the hostname is active/enabled")

def provide_noip_duc_setup():
    """Provide No-IP Dynamic Update Client setup"""
    print("\n🔄 No-IP Dynamic Update Client (DUC)")
    print("=" * 45)
    
    print("📥 Download and Install:")
    print("   • Go to: https://www.noip.com/download")
    print("   • Download 'No-IP DUC for Windows'")
    print("   • Install the application")
    
    print("\n⚙️  Configuration:")
    print("   • Launch No-IP DUC")
    print("   • Enter your No-IP username and password")
    print("   • Select 'scratchgpt.webhop.me' from the hostname list")
    print("   • Click 'Save' to start automatic updates")
    
    print("\n✅ Benefits of DUC:")
    print("   • Automatically updates IP when it changes")
    print("   • Runs as Windows service")
    print("   • Ensures minimal downtime")
    print("   • Handles ISP IP changes automatically")

def check_current_dns_status():
    """Check current DNS status"""
    domain = "scratchgpt.webhop.me"
    public_ip = get_public_ip()
    
    print(f"\n🔍 Current DNS Status")
    print("=" * 30)
    
    resolved_ip = check_dns_resolution(domain)
    
    if resolved_ip:
        print(f"Domain: {domain}")
        print(f"Resolves to: {resolved_ip}")
        print(f"Your public IP: {public_ip}")
        
        if resolved_ip == public_ip:
            print("✅ DNS is correctly configured!")
            return True
        else:
            print("⚠️  DNS mismatch - needs updating")
            return False
    else:
        print(f"❌ {domain} does not resolve")
        print("   Please check your No-IP configuration")
        return False

def provide_troubleshooting_guide():
    """Provide DNS troubleshooting guide"""
    print("\n🔧 DNS Troubleshooting Guide")
    print("=" * 35)
    
    print("❌ Domain not resolving:")
    print("   • Check No-IP account is active")
    print("   • Verify hostname is enabled")
    print("   • Ensure correct spelling of domain")
    print("   • Wait for DNS propagation (up to 24 hours)")
    
    print("\n❌ Wrong IP address:")
    print("   • Update IP in No-IP control panel")
    print("   • Install No-IP DUC for automatic updates")
    print("   • Check if ISP changed your public IP")
    print("   • Verify router has public IP (not behind CGNAT)")
    
    print("\n❌ Slow DNS updates:")
    print("   • Use No-IP DUC for faster updates")
    print("   • Check TTL settings (lower = faster updates)")
    print("   • Consider upgrading to No-IP Plus for faster propagation")
    
    print("\n❌ CGNAT Issues:")
    print("   • Contact ISP to get public IP")
    print("   • Consider VPN with port forwarding")
    print("   • Use Cloudflare Tunnel as alternative")

def test_external_connectivity():
    """Test external connectivity"""
    domain = "scratchgpt.webhop.me"
    port = 8442
    
    print(f"\n🧪 Testing External Connectivity")
    print("=" * 35)
    
    print("📱 Manual Tests:")
    print(f"   • From external network: https://{domain}:{port}")
    print("   • Use mobile data or different internet connection")
    print("   • Should reach ScratchV3 login page")
    
    print("\n🌐 Online Testing Tools:")
    print("   • Port Checker: https://www.yougetsignal.com/tools/open-ports/")
    print("   • DNS Checker: https://dnschecker.org/")
    print("   • SSL Checker: https://www.sslshopper.com/ssl-checker.html")
    
    print(f"\n🔍 Command Line Tests:")
    print(f"   • nslookup {domain}")
    print(f"   • ping {domain}")
    print(f"   • telnet {domain} {port}")

def create_dns_monitoring_script():
    """Create a DNS monitoring script"""
    script_content = '''#!/usr/bin/env python3
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
'''
    
    with open('scripts/monitor_dns.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("\n📝 Created DNS monitoring script: scripts/monitor_dns.py")

def main():
    """Main function"""
    print("🌍 No-IP Dynamic DNS Configuration")
    print("=" * 50)
    
    # Check current status
    dns_ok = check_current_dns_status()
    
    # Provide configuration steps
    provide_noip_configuration_steps()
    
    # Provide DUC setup
    provide_noip_duc_setup()
    
    # Test DNS propagation if configured
    public_ip = get_public_ip()
    if public_ip and dns_ok:
        test_dns_propagation("scratchgpt.webhop.me", public_ip)
    
    # Provide troubleshooting
    provide_troubleshooting_guide()
    
    # Test connectivity
    test_external_connectivity()
    
    # Create monitoring script
    create_dns_monitoring_script()
    
    print("\n" + "=" * 50)
    print("📋 NO-IP DNS CONFIGURATION CHECKLIST")
    print("=" * 50)
    print("□ 1. Log in to No-IP account")
    print("□ 2. Update scratchgpt.webhop.me IP address")
    print("□ 3. Install No-IP DUC for automatic updates")
    print("□ 4. Verify DNS resolution")
    print("□ 5. Test external connectivity")
    print("□ 6. Monitor DNS with scripts/monitor_dns.py")
    
    print(f"\n🎯 Configuration Summary:")
    print(f"   Domain: scratchgpt.webhop.me")
    print(f"   Public IP: {public_ip if public_ip else 'Unknown'}")
    print(f"   Target URL: https://scratchgpt.webhop.me:8442")
    print(f"   DNS Status: {'✅ Configured' if dns_ok else '⚠️  Needs Configuration'}")

if __name__ == "__main__":
    main()
