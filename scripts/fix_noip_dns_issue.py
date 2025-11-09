#!/usr/bin/env python3
"""
No-IP DNS Issue Resolution Guide
Specific steps to fix scratchgpt.webhop.me DNS resolution failure
"""
import requests
import socket
import time
from datetime import datetime

def check_noip_account_status():
    """Provide steps to check No-IP account status"""
    print("🔍 No-IP Account Status Check")
    print("=" * 35)
    
    print("📋 Step-by-Step Account Verification:")
    print("\n1️⃣  Access No-IP Account:")
    print("   • Go to: https://www.noip.com")
    print("   • Click 'Login' (top right)")
    print("   • Enter your username and password")
    
    print("\n2️⃣  Check Account Status:")
    print("   • Look for any warning messages on dashboard")
    print("   • Check if account is 'Active' or 'Suspended'")
    print("   • Verify email address is confirmed")
    
    print("\n3️⃣  Check Billing Status:")
    print("   • Go to 'Account' → 'Billing'")
    print("   • Verify no outstanding payments")
    print("   • Check subscription status")
    
    print("\n4️⃣  Check Hostname Status:")
    print("   • Go to 'Dynamic DNS' → 'No-IP Hostnames'")
    print("   • Look for 'scratchgpt.webhop.me' in the list")
    print("   • Check status column (should be 'Active')")

def check_hostname_configuration():
    """Guide to check hostname configuration"""
    print("\n🌐 Hostname Configuration Check")
    print("=" * 35)
    
    current_ip = get_current_public_ip()
    
    print("📋 Hostname Verification Steps:")
    print("\n1️⃣  Navigate to Hostnames:")
    print("   • In No-IP dashboard: 'Dynamic DNS' → 'No-IP Hostnames'")
    print("   • Find 'scratchgpt.webhop.me' in the list")
    
    print("\n2️⃣  Check Hostname Details:")
    print("   • Status: Should be 'Active' (not Expired/Suspended)")
    print("   • Type: Should be 'A' (Host record)")
    print(f"   • IP Address: Should be {current_ip}")
    print("   • Last Update: Should be recent")
    
    print("\n3️⃣  If Hostname is Missing:")
    print("   • Click 'Create Hostname'")
    print("   • Hostname: scratchgpt.webhop.me")
    print("   • Domain: webhop.me")
    print(f"   • IP Address: {current_ip}")
    print("   • Record Type: A (Host)")
    
    print("\n4️⃣  If IP Address is Wrong:")
    print("   • Click 'Modify' next to scratchgpt.webhop.me")
    print(f"   • Update IP Address to: {current_ip}")
    print("   • Click 'Update Hostname'")

def get_current_public_ip():
    """Get current public IP"""
    try:
        response = requests.get('https://api.ipify.org', timeout=10)
        return response.text.strip()
    except:
        return "197.92.227.126"  # Fallback to last known IP

def check_free_account_limitations():
    """Check for free account limitations"""
    print("\n⚠️  Free Account Limitations")
    print("=" * 35)
    
    print("📋 No-IP Free Account Rules:")
    print("\n🕐 30-Day Confirmation Requirement:")
    print("   • Free hostnames must be confirmed every 30 days")
    print("   • No-IP sends email reminders")
    print("   • Failure to confirm = hostname suspension")
    
    print("\n📧 Check Your Email:")
    print("   • Look for emails from 'no-reply@noip.com'")
    print("   • Subject: 'No-IP Free Dynamic DNS Confirmation'")
    print("   • Click confirmation link if found")
    
    print("\n🔄 Manual Confirmation:")
    print("   • In No-IP dashboard, look for confirmation notices")
    print("   • Click 'Confirm' button if present")
    print("   • This resets the 30-day timer")

def provide_immediate_fixes():
    """Provide immediate fix options"""
    print("\n🚀 Immediate Fix Options")
    print("=" * 30)
    
    current_ip = get_current_public_ip()
    
    print("🔧 Option 1: Update/Recreate Hostname")
    print("1. Log in to No-IP account")
    print("2. Delete existing 'scratchgpt.webhop.me' (if present)")
    print("3. Create new hostname:")
    print("   • Hostname: scratchgpt")
    print("   • Domain: webhop.me")
    print(f"   • IP Address: {current_ip}")
    print("   • Record Type: A")
    print("4. Save and wait 5-10 minutes")
    
    print("\n🔧 Option 2: Use No-IP DUC")
    print("1. Download No-IP Dynamic Update Client")
    print("2. Install and configure with your credentials")
    print("3. Select 'scratchgpt.webhop.me' hostname")
    print("4. Click 'Force Update' to immediately update IP")
    
    print("\n🔧 Option 3: Manual IP Update")
    print("1. Find 'scratchgpt.webhop.me' in hostname list")
    print("2. Click 'Modify'")
    print(f"3. Change IP address to: {current_ip}")
    print("4. Save changes")

def test_dns_resolution_recovery():
    """Test DNS resolution recovery"""
    print("\n🧪 Testing DNS Resolution Recovery")
    print("=" * 40)
    
    domain = "scratchgpt.webhop.me"
    max_attempts = 10
    
    print(f"Testing {domain} resolution...")
    print("This may take several minutes after No-IP update")
    
    for attempt in range(1, max_attempts + 1):
        try:
            resolved_ip = socket.gethostbyname(domain)
            print(f"✅ Attempt {attempt}: {domain} → {resolved_ip}")
            return True
        except socket.gaierror:
            print(f"❌ Attempt {attempt}: DNS resolution failed")
            if attempt < max_attempts:
                print(f"   Waiting 30 seconds before retry...")
                time.sleep(30)
    
    print(f"\n⚠️  DNS still not resolving after {max_attempts} attempts")
    print("   This may take up to 24 hours for full propagation")
    return False

def create_dns_recovery_monitor():
    """Create a DNS recovery monitoring script"""
    script_content = '''#!/usr/bin/env python3
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
                    print(f"\\n🎉 DNS RECOVERY CONFIRMED!")
                    print(f"   {domain} is now resolving consistently")
                    print(f"   You can now test: https://{domain}:8442")
                    break
                    
            except socket.gaierror:
                consecutive_successes = 0
                print(f"[{current_time}] ❌ {domain} - Still not resolving")
            
            time.sleep(60)  # Check every minute
            
        except KeyboardInterrupt:
            print("\\n👋 Monitoring stopped")
            break

if __name__ == "__main__":
    monitor_dns_recovery()
'''
    
    with open('scripts/monitor_dns_recovery.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("\n📝 Created DNS recovery monitor: scripts/monitor_dns_recovery.py")

def provide_alternative_solutions():
    """Provide alternative solutions if No-IP fails"""
    print("\n🔄 Alternative Solutions")
    print("=" * 25)
    
    print("🌐 Option 1: Use Different Dynamic DNS Provider")
    print("   • DuckDNS (free): https://www.duckdns.org")
    print("   • Dynu (free): https://www.dynu.com")
    print("   • FreeDNS (free): https://freedns.afraid.org")
    
    print("\n🌐 Option 2: Use Cloudflare Tunnel")
    print("   • Free secure tunnel to your application")
    print("   • No port forwarding required")
    print("   • Built-in SSL certificates")
    
    print("\n🌐 Option 3: Use ngrok (temporary)")
    print("   • Quick temporary public URL")
    print("   • Good for testing and demos")
    print("   • Command: ngrok http 8081")

def main():
    """Main troubleshooting function"""
    print("🔧 No-IP DNS Issue Resolution Guide")
    print("=" * 40)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    current_ip = get_current_public_ip()
    print(f"🌐 Your current public IP: {current_ip}")
    
    # Provide step-by-step resolution
    check_noip_account_status()
    check_hostname_configuration()
    check_free_account_limitations()
    provide_immediate_fixes()
    
    # Create monitoring tools
    create_dns_recovery_monitor()
    
    # Test DNS resolution
    print("\n" + "=" * 50)
    print("🧪 TESTING DNS RESOLUTION")
    print("=" * 50)
    
    try:
        resolved_ip = socket.gethostbyname("scratchgpt.webhop.me")
        print(f"✅ scratchgpt.webhop.me resolves to: {resolved_ip}")
        if resolved_ip == current_ip:
            print("✅ IP addresses match - DNS is working!")
        else:
            print(f"⚠️  IP mismatch - update No-IP from {resolved_ip} to {current_ip}")
    except socket.gaierror:
        print("❌ scratchgpt.webhop.me is still not resolving")
        print("   Follow the steps above to fix No-IP configuration")
    
    # Provide alternatives
    provide_alternative_solutions()
    
    # Final instructions
    print("\n" + "=" * 50)
    print("📋 ACTION PLAN")
    print("=" * 50)
    print("1. ✅ ScratchV3 application is running locally")
    print("2. 🔧 Fix No-IP DNS configuration:")
    print("   • Log in to No-IP account")
    print("   • Check/update scratchgpt.webhop.me hostname")
    print(f"   • Set IP address to: {current_ip}")
    print("   • Confirm hostname if required")
    print("3. 🔍 Monitor recovery:")
    print("   • Run: python scripts/monitor_dns_recovery.py")
    print("4. 🧪 Test external access:")
    print("   • Wait 5-10 minutes after No-IP update")
    print("   • Test: https://scratchgpt.webhop.me:8442")
    
    print(f"\n🎯 Expected Result:")
    print(f"   External URL: https://scratchgpt.webhop.me:8442")
    print(f"   Should reach ScratchV3 login page")

if __name__ == "__main__":
    main()
