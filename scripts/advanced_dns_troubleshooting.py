#!/usr/bin/env python3
"""
Advanced DNS Troubleshooting for ScratchV3 External Access
Comprehensive DNS propagation testing and alternative verification methods
"""
import subprocess
import requests
import socket
import time
import json
from datetime import datetime
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_dns_propagation_worldwide():
    """Test DNS propagation from multiple global locations"""
    print("🌍 Testing Global DNS Propagation")
    print("=" * 40)
    
    # Online DNS propagation checkers
    online_tools = [
        "https://dnschecker.org/",
        "https://www.whatsmydns.net/",
        "https://dns.google/resolve?name=scratchgpt.webhop.me&type=A",
        "https://1.1.1.1/dns-query?name=scratchgpt.webhop.me&type=A"
    ]
    
    print("🌐 Online DNS Propagation Tools:")
    for tool in online_tools:
        print(f"   • {tool}")
    
    # Test Google DNS API
    try:
        print("\n🔍 Testing Google DNS API:")
        response = requests.get(
            "https://dns.google/resolve?name=scratchgpt.webhop.me&type=A",
            headers={"Accept": "application/dns-json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "Answer" in data:
                for answer in data["Answer"]:
                    if answer["type"] == 1:  # A record
                        print(f"✅ Google DNS: {answer['data']}")
                        return answer['data']
            else:
                print("❌ Google DNS: No A record found")
        else:
            print(f"❌ Google DNS API error: {response.status_code}")
    except Exception as e:
        print(f"❌ Google DNS API error: {e}")
    
    # Test Cloudflare DNS API
    try:
        print("\n🔍 Testing Cloudflare DNS API:")
        response = requests.get(
            "https://1.1.1.1/dns-query?name=scratchgpt.webhop.me&type=A",
            headers={"Accept": "application/dns-json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "Answer" in data:
                for answer in data["Answer"]:
                    if answer["type"] == 1:  # A record
                        print(f"✅ Cloudflare DNS: {answer['data']}")
                        return answer['data']
            else:
                print("❌ Cloudflare DNS: No A record found")
        else:
            print(f"❌ Cloudflare DNS API error: {response.status_code}")
    except Exception as e:
        print(f"❌ Cloudflare DNS API error: {e}")
    
    return None

def test_direct_dns_servers():
    """Test against specific DNS servers"""
    print("\n🔍 Testing Specific DNS Servers")
    print("=" * 35)
    
    dns_servers = [
        ("Google Primary", "8.8.8.8"),
        ("Google Secondary", "8.8.4.4"),
        ("Cloudflare Primary", "1.1.1.1"),
        ("Cloudflare Secondary", "1.0.0.1"),
        ("OpenDNS Primary", "208.67.222.222"),
        ("OpenDNS Secondary", "208.67.220.220"),
        ("Quad9", "9.9.9.9"),
        ("Level3", "4.2.2.2")
    ]
    
    results = {}
    
    for name, server in dns_servers:
        try:
            cmd = ['nslookup', 'scratchgpt.webhop.me', server]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            # Parse nslookup output
            lines = result.stdout.split('\n')
            ip_found = None
            for line in lines:
                if 'Address:' in line and '::' not in line and '#' not in line:
                    parts = line.split('Address:')
                    if len(parts) > 1:
                        ip_found = parts[-1].strip()
                        break
            
            if ip_found and ip_found != server:
                results[name] = ip_found
                print(f"✅ {name} ({server}): {ip_found}")
            else:
                results[name] = "No response"
                print(f"❌ {name} ({server}): No response")
                
        except Exception as e:
            results[name] = f"Error: {e}"
            print(f"❌ {name} ({server}): Error - {e}")
    
    return results

def test_alternative_access_methods():
    """Test alternative ways to access the application"""
    print("\n🔄 Testing Alternative Access Methods")
    print("=" * 40)
    
    public_ip = "197.92.227.126"
    
    print("🌐 Direct IP Access Tests:")
    
    # Test direct IP access
    direct_urls = [
        f"https://{public_ip}:8442",
        f"http://{public_ip}:8442"
    ]
    
    for url in direct_urls:
        try:
            print(f"\n🔍 Testing: {url}")
            response = requests.get(f"{url}/health", timeout=10, verify=False)
            if response.status_code == 200:
                print(f"✅ Direct IP access working: {url}")
                print(f"   Response: {response.text[:100]}...")
                return True
            else:
                print(f"⚠️  {url} returned status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {url} - Connection refused")
        except requests.exceptions.Timeout:
            print(f"❌ {url} - Timeout")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
    
    return False

def check_no_ip_service_status():
    """Check No-IP service status and potential issues"""
    print("\n🔍 Checking No-IP Service Status")
    print("=" * 35)
    
    # Check No-IP status page
    try:
        response = requests.get("https://status.noip.com", timeout=10)
        if response.status_code == 200:
            print("✅ No-IP status page accessible")
        else:
            print(f"⚠️  No-IP status page returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach No-IP status page: {e}")
    
    # Check No-IP main site
    try:
        response = requests.get("https://www.noip.com", timeout=10)
        if response.status_code == 200:
            print("✅ No-IP main site accessible")
        else:
            print(f"⚠️  No-IP main site returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach No-IP main site: {e}")
    
    print("\n📋 Common No-IP Issues:")
    print("• DNS propagation delay (normal: 5-60 minutes)")
    print("• Free account confirmation required")
    print("• Hostname suspended due to inactivity")
    print("• No-IP service maintenance")
    print("• ISP DNS caching issues")

def test_local_dns_cache():
    """Test and clear local DNS cache"""
    print("\n🔄 Testing Local DNS Cache")
    print("=" * 30)
    
    print("📋 DNS Cache Information:")
    
    # Display DNS cache (Windows)
    try:
        result = subprocess.run(
            ["ipconfig", "/displaydns"],
            capture_output=True, text=True, timeout=10
        )
        
        if "scratchgpt.webhop.me" in result.stdout:
            print("⚠️  scratchgpt.webhop.me found in local DNS cache")
            print("   This might be caching old/invalid data")
        else:
            print("✅ scratchgpt.webhop.me not in local DNS cache")
            
    except Exception as e:
        print(f"❌ Cannot check DNS cache: {e}")
    
    print("\n🔧 DNS Cache Management:")
    print("To clear DNS cache, run as Administrator:")
    print("   ipconfig /flushdns")
    
    # Attempt to flush DNS cache
    try:
        result = subprocess.run(
            ["ipconfig", "/flushdns"],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            print("✅ DNS cache flushed successfully")
        else:
            print("⚠️  DNS cache flush may have failed")
            
    except Exception as e:
        print(f"❌ Cannot flush DNS cache: {e}")
        print("   Please run 'ipconfig /flushdns' as Administrator")

def provide_propagation_timeline():
    """Provide realistic DNS propagation timeline"""
    print("\n⏰ DNS Propagation Timeline")
    print("=" * 30)
    
    current_time = datetime.now()
    
    print("📅 Typical DNS Propagation Times:")
    print("• Local ISP DNS: 5-15 minutes")
    print("• Major DNS providers: 15-30 minutes") 
    print("• Global propagation: 1-4 hours")
    print("• Complete propagation: Up to 24-48 hours")
    
    print("\n🕐 No-IP Specific Times:")
    print("• No-IP DNS servers: 1-5 minutes")
    print("• ISP cache refresh: 15-60 minutes")
    print("• Global DNS cache: 2-6 hours")
    
    print(f"\n📊 Current Status (as of {current_time.strftime('%H:%M:%S')}):")
    print("• If updated <30 min ago: Normal delay")
    print("• If updated 30-60 min ago: Possible ISP caching")
    print("• If updated >60 min ago: Investigate further")

def create_comprehensive_test_script():
    """Create a comprehensive testing script"""
    script_content = '''#!/usr/bin/env python3
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
    print("\\n1️⃣  Testing Local Application:")
    try:
        response = requests.get('https://192.168.1.4:8081/health', verify=False, timeout=5)
        print(f"   ✅ Local app: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Local app: {e}")
        return
    
    # Test 2: DNS resolution
    print("\\n2️⃣  Testing DNS Resolution:")
    try:
        ip = socket.gethostbyname('scratchgpt.webhop.me')
        print(f"   ✅ DNS resolves to: {ip}")
        dns_working = True
    except:
        print(f"   ❌ DNS resolution failed")
        dns_working = False
    
    # Test 3: Direct IP access
    print("\\n3️⃣  Testing Direct IP Access:")
    try:
        response = requests.get('https://197.92.227.126:8442/health', verify=False, timeout=10)
        print(f"   ✅ Direct IP: Status {response.status_code}")
        direct_working = True
    except Exception as e:
        print(f"   ❌ Direct IP: {e}")
        direct_working = False
    
    # Test 4: Domain access (if DNS working)
    if dns_working:
        print("\\n4️⃣  Testing Domain Access:")
        try:
            response = requests.get('https://scratchgpt.webhop.me:8442/health', verify=False, timeout=10)
            print(f"   ✅ Domain access: Status {response.status_code}")
            print("   🎉 EXTERNAL ACCESS WORKING!")
        except Exception as e:
            print(f"   ❌ Domain access: {e}")
    
    # Summary
    print("\\n📊 Test Summary:")
    print(f"   Local App: {'✅' if True else '❌'}")
    print(f"   DNS Resolution: {'✅' if dns_working else '❌'}")
    print(f"   Direct IP Access: {'✅' if direct_working else '❌'}")
    
    if dns_working and direct_working:
        print("\\n🎯 Result: External access should be working!")
        print("   Try: https://scratchgpt.webhop.me:8442")
    elif direct_working and not dns_working:
        print("\\n🎯 Result: Router/app working, DNS propagation needed")
        print("   Wait for DNS propagation or use direct IP")
    else:
        print("\\n🎯 Result: Check router port forwarding")

if __name__ == "__main__":
    comprehensive_test()
'''
    
    with open('scripts/comprehensive_test.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("\n📝 Created comprehensive test: scripts/comprehensive_test.py")

def main():
    """Main advanced troubleshooting function"""
    print("🔍 Advanced DNS Troubleshooting for ScratchV3")
    print("=" * 50)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test global DNS propagation
    global_ip = test_dns_propagation_worldwide()
    
    # Test specific DNS servers
    dns_results = test_direct_dns_servers()
    
    # Test alternative access methods
    direct_access = test_alternative_access_methods()
    
    # Check No-IP service status
    check_no_ip_service_status()
    
    # Test local DNS cache
    test_local_dns_cache()
    
    # Provide propagation timeline
    provide_propagation_timeline()
    
    # Create comprehensive test script
    create_comprehensive_test_script()
    
    # Analysis and recommendations
    print("\n" + "=" * 50)
    print("📊 ANALYSIS & RECOMMENDATIONS")
    print("=" * 50)
    
    if global_ip:
        print(f"✅ DNS is working in some locations: {global_ip}")
        print("🎯 ISSUE: Local DNS propagation delay")
        print("📋 SOLUTIONS:")
        print("   • Wait 15-30 more minutes")
        print("   • Clear local DNS cache: ipconfig /flushdns")
        print("   • Try different DNS servers (8.8.8.8)")
        print("   • Test from mobile data/external network")
        
    elif direct_access:
        print("✅ Direct IP access working")
        print("🎯 ISSUE: DNS propagation not complete")
        print("📋 SOLUTIONS:")
        print("   • Wait for global DNS propagation (1-4 hours)")
        print("   • Use direct IP temporarily: https://197.92.227.126:8442")
        print("   • Check No-IP account for issues")
        
    else:
        print("❌ Neither DNS nor direct IP working")
        print("🎯 ISSUE: Router or application problem")
        print("📋 SOLUTIONS:")
        print("   • Verify router port forwarding")
        print("   • Check Windows Firewall")
        print("   • Restart ScratchV3 application")
    
    print(f"\n🔧 Next Steps:")
    print(f"1. Run: python scripts/comprehensive_test.py")
    print(f"2. Test from external network (mobile data)")
    print(f"3. Wait for DNS propagation (up to 4 hours)")
    print(f"4. Monitor with: python scripts/monitor_dns_recovery.py")

if __name__ == "__main__":
    main()
