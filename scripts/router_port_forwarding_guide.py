#!/usr/bin/env python3
"""
Router Port Forwarding Configuration Guide
Provides detailed instructions for setting up port forwarding for ScratchV3 external access
"""
import subprocess
import socket
import requests

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
        
        # Get default gateway (router IP)
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        gateway_ip = None
        for line in result.stdout.split('\n'):
            if 'Default Gateway' in line and '192.168' in line:
                gateway_ip = line.split(':')[-1].strip()
                break
        
        return local_ip, public_ip, gateway_ip
        
    except Exception as e:
        print(f"Error getting network info: {e}")
        return "192.168.1.4", "Unknown", "192.168.1.1"

def detect_router_brand():
    """Try to detect router brand from gateway IP"""
    local_ip, public_ip, gateway_ip = get_network_info()
    
    print("🌐 Network Information")
    print("=" * 30)
    print(f"Local IP: {local_ip}")
    print(f"Public IP: {public_ip}")
    print(f"Router IP: {gateway_ip}")
    
    return local_ip, public_ip, gateway_ip

def provide_generic_instructions(local_ip, gateway_ip):
    """Provide generic port forwarding instructions"""
    print("\n🔧 Generic Port Forwarding Setup")
    print("=" * 40)
    
    print("📋 Required Settings:")
    print(f"   Service Name: ScratchV3-HTTPS")
    print(f"   External Port: 8442")
    print(f"   Internal IP: {local_ip}")
    print(f"   Internal Port: 8081")
    print(f"   Protocol: TCP")
    print(f"   Status: Enabled")
    
    print("\n🌐 Access Router Admin Panel:")
    print(f"1. Open browser and go to: http://{gateway_ip}")
    print("2. Login with admin credentials (check router label)")
    print("3. Look for one of these sections:")
    print("   • Port Forwarding")
    print("   • Virtual Server")
    print("   • NAT Forwarding")
    print("   • Applications & Gaming")
    print("   • Advanced → NAT")

def provide_brand_specific_instructions():
    """Provide brand-specific router instructions"""
    print("\n🏷️  Brand-Specific Instructions")
    print("=" * 40)
    
    print("🔸 LINKSYS Routers:")
    print("   1. Smart Wi-Fi Tools → Priority")
    print("   2. Gaming → Single Port Forwarding")
    print("   3. Add new rule with settings above")
    
    print("\n🔸 NETGEAR Routers:")
    print("   1. Dynamic DNS → Port Forwarding")
    print("   2. Add Custom Service")
    print("   3. Enter port forwarding details")
    
    print("\n🔸 TP-LINK Routers:")
    print("   1. Advanced → NAT Forwarding")
    print("   2. Port Forwarding")
    print("   3. Add new forwarding rule")
    
    print("\n🔸 ASUS Routers:")
    print("   1. Adaptive QoS → Traditional QoS")
    print("   2. Port Forwarding")
    print("   3. Enable port forwarding and add rule")
    
    print("\n🔸 D-LINK Routers:")
    print("   1. Advanced → Port Forwarding")
    print("   2. Add new rule")
    print("   3. Configure with required settings")
    
    print("\n🔸 BELKIN Routers:")
    print("   1. Firewall → Virtual Servers")
    print("   2. Add new virtual server")
    print("   3. Enter port forwarding configuration")

def provide_troubleshooting_tips():
    """Provide troubleshooting tips"""
    print("\n🔧 Troubleshooting Tips")
    print("=" * 30)
    
    print("❌ Can't access router admin panel:")
    print("   • Try 192.168.0.1 or 192.168.1.1")
    print("   • Check router label for default IP/credentials")
    print("   • Reset router to factory defaults if needed")
    
    print("\n❌ Port forwarding not working:")
    print("   • Restart router after configuration")
    print("   • Check if UPnP is enabled (may conflict)")
    print("   • Verify internal IP hasn't changed")
    print("   • Test with online port checker tools")
    
    print("\n❌ Multiple devices on network:")
    print("   • Ensure IP address is static or reserved")
    print("   • Check DHCP reservation settings")
    print("   • Verify no IP conflicts exist")

def test_port_forwarding(local_ip):
    """Test if port forwarding is working"""
    print("\n🧪 Testing Port Forwarding")
    print("=" * 30)
    
    print("📱 Manual Tests:")
    print("1. From external network (mobile data):")
    print("   • Try: https://scratchgpt.webhop.me:8442")
    print("   • Should reach ScratchV3 login page")
    
    print("\n🌐 Online Testing Tools:")
    print("   • Port Checker: https://www.yougetsignal.com/tools/open-ports/")
    print(f"   • Test IP: [Your Public IP]")
    print("   • Test Port: 8442")
    
    print("\n🔍 Local Verification:")
    print(f"   • Verify app running: https://{local_ip}:8081")
    print("   • Check Windows Firewall allows port 8081")
    print("   • Ensure router firewall allows port 8442")

def provide_security_considerations():
    """Provide security considerations"""
    print("\n🛡️  Security Considerations")
    print("=" * 35)
    
    print("✅ Recommended Security Settings:")
    print("   • Use non-standard external port (8442)")
    print("   • Enable HTTPS only (SSL certificate)")
    print("   • Configure strong authentication")
    print("   • Monitor access logs regularly")
    print("   • Keep application updated")
    
    print("\n⚠️  Additional Security:")
    print("   • Consider VPN access instead of port forwarding")
    print("   • Use Cloudflare Tunnel for enhanced security")
    print("   • Enable fail2ban or similar intrusion detection")
    print("   • Regular security audits")

def create_port_forwarding_script():
    """Create a verification script"""
    script_content = '''#!/usr/bin/env python3
"""
Port Forwarding Verification Script
"""
import socket
import requests

def test_external_access():
    """Test external access"""
    try:
        response = requests.get('https://scratchgpt.webhop.me:8442/health', 
                              timeout=10, verify=False)
        if response.status_code == 200:
            print("✅ External access working!")
            return True
        else:
            print(f"⚠️  External access returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ External access failed: {e}")
        return False

def test_port_open():
    """Test if port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('scratchgpt.webhop.me', 8442))
        sock.close()
        if result == 0:
            print("✅ Port 8442 is open")
            return True
        else:
            print("❌ Port 8442 is closed")
            return False
    except Exception as e:
        print(f"❌ Port test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing External Access")
    print("=" * 30)
    test_port_open()
    test_external_access()
'''
    
    with open('scripts/test_external_access.py', 'w') as f:
        f.write(script_content)
    
    print("\n📝 Created verification script: scripts/test_external_access.py")

def main():
    """Main function"""
    print("🌐 Router Port Forwarding Configuration Guide")
    print("=" * 50)
    
    # Get network information
    local_ip, public_ip, gateway_ip = detect_router_brand()
    
    # Provide instructions
    provide_generic_instructions(local_ip, gateway_ip)
    provide_brand_specific_instructions()
    provide_troubleshooting_tips()
    test_port_forwarding(local_ip)
    provide_security_considerations()
    
    # Create verification script
    create_port_forwarding_script()
    
    print("\n" + "=" * 50)
    print("📋 PORT FORWARDING CHECKLIST")
    print("=" * 50)
    print("□ 1. Access router admin panel")
    print("□ 2. Navigate to Port Forwarding section")
    print("□ 3. Create new rule:")
    print(f"     • External Port: 8442")
    print(f"     • Internal IP: {local_ip}")
    print(f"     • Internal Port: 8081")
    print(f"     • Protocol: TCP")
    print("□ 4. Save and restart router")
    print("□ 5. Test with: python scripts/test_external_access.py")
    
    print(f"\n🎯 Target Configuration:")
    print(f"   External: https://scratchgpt.webhop.me:8442")
    print(f"   Internal: https://{local_ip}:8081")
    print(f"   Router: {gateway_ip}")

if __name__ == "__main__":
    main()
