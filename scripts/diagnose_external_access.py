#!/usr/bin/env python3
"""
ScratchV3 External Access Diagnostic Tool
Diagnoses DNS, IP, and connectivity issues for external access
"""
import requests
import socket
import subprocess
import time
import json
from datetime import datetime
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_current_public_ip():
    """Get current public IP from multiple sources"""
    print("🌐 Checking Current Public IP")
    print("=" * 35)
    
    ip_services = [
        ("ipify.org", "https://api.ipify.org"),
        ("httpbin.org", "https://httpbin.org/ip"),
        ("icanhazip.com", "https://icanhazip.com"),
        ("ipecho.net", "https://ipecho.net/plain")
    ]
    
    current_ips = []
    
    for service_name, url in ip_services:
        try:
            if "httpbin" in url:
                response = requests.get(url, timeout=10)
                ip = json.loads(response.text)['origin'].split(',')[0].strip()
            else:
                response = requests.get(url, timeout=10)
                ip = response.text.strip()
            
            current_ips.append(ip)
            print(f"✅ {service_name}: {ip}")
            
        except Exception as e:
            print(f"❌ {service_name}: Error - {e}")
    
    if current_ips:
        # Check if all IPs are the same
        unique_ips = list(set(current_ips))
        if len(unique_ips) == 1:
            print(f"\n🎯 Confirmed Public IP: {unique_ips[0]}")
            return unique_ips[0]
        else:
            print(f"\n⚠️  Multiple IPs detected: {unique_ips}")
            return unique_ips[0]  # Return the first one
    else:
        print("\n❌ Could not determine public IP")
        return None

def check_dns_resolution():
    """Check DNS resolution for scratchgpt.webhop.me"""
    print("\n🔍 Checking DNS Resolution")
    print("=" * 30)
    
    domain = "scratchgpt.webhop.me"
    
    try:
        resolved_ip = socket.gethostbyname(domain)
        print(f"✅ {domain} resolves to: {resolved_ip}")
        return resolved_ip
    except socket.gaierror as e:
        print(f"❌ {domain} DNS resolution failed: {e}")
        return None

def test_dns_propagation():
    """Test DNS propagation across multiple DNS servers"""
    print("\n🌍 Testing DNS Propagation")
    print("=" * 30)
    
    domain = "scratchgpt.webhop.me"
    dns_servers = [
        ("Google DNS", "8.8.8.8"),
        ("Cloudflare DNS", "1.1.1.1"),
        ("OpenDNS", "208.67.222.222"),
        ("Quad9 DNS", "9.9.9.9"),
        ("Your ISP DNS", "")  # Use system default
    ]
    
    results = {}
    
    for name, server in dns_servers:
        try:
            if server:  # Use specific DNS server
                cmd = ['nslookup', domain, server]
            else:  # Use system default DNS
                cmd = ['nslookup', domain]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            # Parse nslookup output to extract IP
            lines = result.stdout.split('\n')
            ip_found = None
            for line in lines:
                if 'Address:' in line and '::' not in line and '#' not in line:
                    ip_found = line.split('Address:')[-1].strip()
                    break
            
            if ip_found:
                results[name] = ip_found
                print(f"✅ {name}: {ip_found}")
            else:
                results[name] = "No response"
                print(f"❌ {name}: No response")
                
        except Exception as e:
            results[name] = f"Error: {e}"
            print(f"❌ {name}: Error - {e}")
    
    return results

def compare_ip_addresses():
    """Compare current public IP with DNS resolution"""
    print("\n📊 IP Address Comparison")
    print("=" * 30)
    
    current_ip = get_current_public_ip()
    resolved_ip = check_dns_resolution()
    
    if current_ip and resolved_ip:
        if current_ip == resolved_ip:
            print(f"✅ IP addresses match!")
            print(f"   Current Public IP: {current_ip}")
            print(f"   DNS Resolved IP: {resolved_ip}")
            return True, current_ip, resolved_ip
        else:
            print(f"❌ IP address mismatch detected!")
            print(f"   Current Public IP: {current_ip}")
            print(f"   DNS Resolved IP: {resolved_ip}")
            print(f"   🔧 Action needed: Update No-IP configuration")
            return False, current_ip, resolved_ip
    else:
        print(f"⚠️  Cannot compare - missing data")
        print(f"   Current Public IP: {current_ip or 'Unknown'}")
        print(f"   DNS Resolved IP: {resolved_ip or 'Failed to resolve'}")
        return False, current_ip, resolved_ip

def test_port_connectivity():
    """Test port connectivity to external domain"""
    print("\n🔌 Testing Port Connectivity")
    print("=" * 30)
    
    domain = "scratchgpt.webhop.me"
    port = 8442
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((domain, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is accessible on {domain}")
            return True
        else:
            print(f"❌ Port {port} is not accessible on {domain}")
            print(f"   Error code: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Port connectivity test failed: {e}")
        return False

def test_local_application():
    """Test local application is still running"""
    print("\n🏠 Testing Local Application")
    print("=" * 30)
    
    local_endpoints = [
        "https://localhost:8081/health",
        "https://127.0.0.1:8081/health",
        "https://192.168.1.4:8081/health"
    ]
    
    working_endpoints = 0
    
    for endpoint in local_endpoints:
        try:
            response = requests.get(endpoint, timeout=5, verify=False)
            if response.status_code == 200:
                print(f"✅ {endpoint}")
                working_endpoints += 1
            else:
                print(f"⚠️  {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    if working_endpoints > 0:
        print(f"\n✅ Local application is running ({working_endpoints}/3 endpoints working)")
        return True
    else:
        print(f"\n❌ Local application appears to be down")
        return False

def check_no_ip_service_status():
    """Check No-IP service status"""
    print("\n🌐 Checking No-IP Service Status")
    print("=" * 35)
    
    try:
        # Try to access No-IP's status page
        response = requests.get("https://www.noip.com", timeout=10)
        if response.status_code == 200:
            print("✅ No-IP service is accessible")
        else:
            print(f"⚠️  No-IP service returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach No-IP service: {e}")
    
    print("\n📋 Manual Verification Steps:")
    print("1. Visit: https://www.noip.com")
    print("2. Log in to your account")
    print("3. Go to 'Dynamic DNS' → 'No-IP Hostnames'")
    print("4. Check 'scratchgpt.webhop.me' status")
    print("5. Verify IP address is current")

def provide_troubleshooting_steps(ip_match, current_ip, resolved_ip):
    """Provide specific troubleshooting steps based on diagnosis"""
    print("\n🔧 Troubleshooting Steps")
    print("=" * 25)
    
    if not ip_match and current_ip and resolved_ip:
        print("🎯 ISSUE IDENTIFIED: IP Address Mismatch")
        print("=" * 45)
        print(f"Your public IP has changed from {resolved_ip} to {current_ip}")
        print("\n📝 SOLUTION:")
        print("1. Log in to your No-IP account at https://www.noip.com")
        print("2. Navigate to 'Dynamic DNS' → 'No-IP Hostnames'")
        print("3. Find 'scratchgpt.webhop.me' and click 'Modify'")
        print(f"4. Update IP address from {resolved_ip} to {current_ip}")
        print("5. Save changes and wait 5-10 minutes for propagation")
        
        print("\n⚡ QUICK FIX (if you have No-IP DUC installed):")
        print("• Open No-IP Dynamic Update Client")
        print("• Click 'Force Update' to immediately update IP")
        
    elif not resolved_ip:
        print("🎯 ISSUE IDENTIFIED: DNS Resolution Failure")
        print("=" * 45)
        print("The domain scratchgpt.webhop.me is not resolving at all")
        print("\n📝 POSSIBLE CAUSES:")
        print("• No-IP hostname expired or suspended")
        print("• Account payment issues")
        print("• Hostname accidentally deleted")
        print("• DNS propagation issues")
        
        print("\n📝 SOLUTION:")
        print("1. Check No-IP account status")
        print("2. Verify hostname is active and not expired")
        print("3. Check account billing status")
        print("4. Re-create hostname if necessary")
        
    else:
        print("🎯 ISSUE: Unknown DNS Problem")
        print("=" * 30)
        print("DNS resolution is failing for unknown reasons")
        print("\n📝 GENERAL TROUBLESHOOTING:")
        print("1. Clear DNS cache: ipconfig /flushdns")
        print("2. Try different DNS servers (8.8.8.8, 1.1.1.1)")
        print("3. Check No-IP account status")
        print("4. Wait for DNS propagation (up to 24 hours)")

def create_monitoring_script():
    """Create a monitoring script to track changes"""
    script_content = f'''#!/usr/bin/env python3
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
            
            print(f"[{{current_time}}] Public: {{public_ip}} | DNS: {{dns_ip}} | {{status}}")
            
            if ip_changed:
                print(f"  🚨 PUBLIC IP CHANGED: {{last_public_ip}} → {{public_ip}}")
            
            if dns_changed:
                print(f"  🚨 DNS IP CHANGED: {{last_dns_ip}} → {{dns_ip}}")
            
            last_public_ip = public_ip
            last_dns_ip = dns_ip
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"  ❌ Error: {{e}}")
            time.sleep(30)

if __name__ == "__main__":
    monitor_changes()
'''
    
    with open('scripts/monitor_realtime.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("\n📝 Created real-time monitoring script: scripts/monitor_realtime.py")

def main():
    """Main diagnostic function"""
    print("🔍 ScratchV3 External Access Diagnostic Tool")
    print("=" * 50)
    print(f"🕐 Diagnostic started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test local application first
    local_ok = test_local_application()
    
    if not local_ok:
        print("\n⚠️  WARNING: Local application issues detected!")
        print("Fix local application before troubleshooting external access")
        return
    
    # Get current network status
    current_ip = get_current_public_ip()
    resolved_ip = check_dns_resolution()
    
    # Compare IPs
    ip_match, current_ip, resolved_ip = compare_ip_addresses()
    
    # Test DNS propagation
    test_dns_propagation()
    
    # Test port connectivity
    port_ok = test_port_connectivity()
    
    # Check No-IP service
    check_no_ip_service_status()
    
    # Provide troubleshooting steps
    provide_troubleshooting_steps(ip_match, current_ip, resolved_ip)
    
    # Create monitoring script
    create_monitoring_script()
    
    # Final summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print(f"✅ Local Application: {'Working' if local_ok else 'Issues'}")
    print(f"{'✅' if current_ip else '❌'} Public IP Detection: {current_ip or 'Failed'}")
    print(f"{'✅' if resolved_ip else '❌'} DNS Resolution: {resolved_ip or 'Failed'}")
    print(f"{'✅' if ip_match else '❌'} IP Match: {'Yes' if ip_match else 'No - Update needed'}")
    print(f"{'✅' if port_ok else '❌'} Port 8442: {'Accessible' if port_ok else 'Not accessible'}")
    
    if not ip_match and current_ip and resolved_ip:
        print(f"\n🎯 PRIMARY ISSUE: IP address changed")
        print(f"   Update No-IP from {resolved_ip} to {current_ip}")
    elif not resolved_ip:
        print(f"\n🎯 PRIMARY ISSUE: DNS resolution completely failed")
        print(f"   Check No-IP account and hostname status")
    
    print(f"\n🔧 Next Steps:")
    print(f"1. Update No-IP configuration if IP changed")
    print(f"2. Run: python scripts/monitor_realtime.py")
    print(f"3. Test again in 5-10 minutes after DNS update")

if __name__ == "__main__":
    main()
