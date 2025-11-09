#!/usr/bin/env python3
"""
Browser Trust Setup for ScratchV3 SSL Certificates
This script provides instructions and automated steps for configuring browser trust
"""
import os
import subprocess
import sys
import webbrowser
from pathlib import Path

def check_certificate_files():
    """Check if certificate files exist"""
    cert_file = "localhost+4.pem"
    key_file = "localhost+4-key.pem"
    
    cert_exists = os.path.exists(cert_file)
    key_exists = os.path.exists(key_file)
    
    print("🔍 Certificate File Check")
    print("=" * 30)
    print(f"Certificate: {'✅' if cert_exists else '❌'} {cert_file}")
    print(f"Private Key: {'✅' if key_exists else '❌'} {key_file}")
    
    return cert_exists and key_exists

def check_mkcert_ca_status():
    """Check if mkcert CA is properly installed"""
    try:
        result = subprocess.run(["mkcert", "-CAROOT"], capture_output=True, text=True)
        if result.returncode == 0:
            ca_root = result.stdout.strip()
            print(f"\n🔐 mkcert CA Status")
            print("=" * 30)
            print(f"✅ CA Root: {ca_root}")
            
            # Check if CA files exist
            ca_cert = os.path.join(ca_root, "rootCA.pem")
            ca_key = os.path.join(ca_root, "rootCA-key.pem")
            
            print(f"CA Certificate: {'✅' if os.path.exists(ca_cert) else '❌'}")
            print(f"CA Key: {'✅' if os.path.exists(ca_key) else '❌'}")
            return True
        else:
            print("❌ mkcert CA not properly configured")
            return False
    except FileNotFoundError:
        print("❌ mkcert not found")
        return False

def provide_browser_instructions():
    """Provide browser-specific trust instructions"""
    print("\n🌐 Browser Trust Configuration")
    print("=" * 50)
    
    print("\n📋 AUTOMATIC TRUST (Recommended)")
    print("Since you're using mkcert, the certificates should already be trusted!")
    print("mkcert automatically installs its CA in your system trust store.")
    
    print("\n🔧 If you still see security warnings:")
    
    print("\n1️⃣  CHROME/EDGE:")
    print("   • Go to: chrome://settings/certificates")
    print("   • Click 'Manage certificates'")
    print("   • Go to 'Trusted Root Certification Authorities'")
    print("   • Look for 'mkcert' certificate")
    print("   • If missing, click 'Import' and select mkcert's rootCA.pem")
    
    print("\n2️⃣  FIREFOX:")
    print("   • Go to: about:preferences#privacy")
    print("   • Scroll to 'Certificates' → 'View Certificates'")
    print("   • Go to 'Authorities' tab")
    print("   • Look for 'mkcert development CA'")
    print("   • If missing, click 'Import' and select mkcert's rootCA.pem")
    
    print("\n3️⃣  SAFARI (macOS):")
    print("   • Open 'Keychain Access'")
    print("   • Look for 'mkcert' in 'System' keychain")
    print("   • Double-click → Trust → 'Always Trust'")

def test_https_endpoints():
    """Test HTTPS endpoints"""
    print("\n🧪 Testing HTTPS Endpoints")
    print("=" * 50)
    
    endpoints = [
        "https://localhost:8081",
        "https://127.0.0.1:8081", 
        "https://192.168.1.4:8081"
    ]
    
    print("📝 Manual Testing Required:")
    print("Please test these URLs in your browser:")
    
    for i, endpoint in enumerate(endpoints, 1):
        print(f"   {i}. {endpoint}")
    
    print("\n✅ Expected Results:")
    print("   • No security warnings")
    print("   • Green padlock icon")
    print("   • ScratchV3 login page loads")
    
    print("\n❌ If you see 'DNS_PROBE_FINISHED_NXDOMAIN':")
    print("   • Clear browser cache (Ctrl+Shift+Delete)")
    print("   • Try incognito/private mode")
    print("   • Restart browser completely")
    print("   • Check Windows Firewall settings")

def provide_firewall_instructions():
    """Provide Windows Firewall configuration instructions"""
    print("\n🛡️  Windows Firewall Configuration")
    print("=" * 50)
    
    print("If you can't access from 192.168.1.4:8081:")
    print("\n1️⃣  Allow Python through Windows Firewall:")
    print("   • Open Windows Defender Firewall")
    print("   • Click 'Allow an app or feature through Windows Defender Firewall'")
    print("   • Click 'Change Settings' → 'Allow another app'")
    print("   • Browse to your Python installation")
    print("   • Check both 'Private' and 'Public' networks")
    
    print("\n2️⃣  Or create specific rule for port 8081:")
    print("   • Open Windows Defender Firewall with Advanced Security")
    print("   • Click 'Inbound Rules' → 'New Rule'")
    print("   • Select 'Port' → 'TCP' → Specific port: 8081")
    print("   • Allow the connection")
    print("   • Apply to all profiles")

def provide_troubleshooting_steps():
    """Provide additional troubleshooting steps"""
    print("\n🔧 Additional Troubleshooting")
    print("=" * 50)
    
    print("1️⃣  Clear DNS Cache:")
    print("   • Open Command Prompt as Administrator")
    print("   • Run: ipconfig /flushdns")
    
    print("\n2️⃣  Reset Browser:")
    print("   • Clear all browsing data")
    print("   • Disable extensions temporarily")
    print("   • Try different browser")
    
    print("\n3️⃣  Check Network:")
    print("   • Ensure you're on the same network")
    print("   • Verify IP address: ipconfig")
    print("   • Test with: ping 192.168.1.4")
    
    print("\n4️⃣  Application Logs:")
    print("   • Check console output when starting app")
    print("   • Look for SSL/certificate errors")
    print("   • Verify port 8081 is not blocked")

def open_test_urls():
    """Open test URLs in default browser"""
    print("\n🚀 Opening Test URLs")
    print("=" * 30)
    
    urls = [
        "https://localhost:8081",
        "https://127.0.0.1:8081"
    ]
    
    for url in urls:
        try:
            print(f"Opening: {url}")
            webbrowser.open(url)
        except Exception as e:
            print(f"Could not open {url}: {e}")

def main():
    """Main function"""
    print("🌐 ScratchV3 Browser Trust Setup")
    print("=" * 50)
    
    # Check certificate files
    if not check_certificate_files():
        print("❌ Certificate files missing. Please run the SSL fix script first.")
        return
    
    # Check mkcert CA status
    ca_ok = check_mkcert_ca_status()
    
    # Provide browser instructions
    provide_browser_instructions()
    
    # Provide firewall instructions
    provide_firewall_instructions()
    
    # Provide troubleshooting steps
    provide_troubleshooting_steps()
    
    print("\n" + "=" * 50)
    print("🎯 QUICK ACTION PLAN")
    print("=" * 50)
    print("1. Restart your ScratchV3 application")
    print("2. Clear browser cache and restart browser")
    print("3. Test URLs in this order:")
    print("   • https://localhost:8081 (should work)")
    print("   • https://127.0.0.1:8081 (should work)")
    print("   • https://192.168.1.4:8081 (check firewall if fails)")
    print("4. If still failing, check Windows Firewall")
    print("5. Try incognito/private browsing mode")
    
    # Ask if user wants to open test URLs
    try:
        choice = input("\n🚀 Open test URLs in browser now? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            open_test_urls()
    except KeyboardInterrupt:
        print("\nSkipping browser test...")

if __name__ == "__main__":
    main()
