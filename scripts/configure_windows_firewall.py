#!/usr/bin/env python3
"""
Windows Firewall Configuration for ScratchV3 External Access
Creates firewall rules to allow external access while maintaining security
"""
import subprocess
import sys
import os

def check_admin_privileges():
    """Check if running with administrator privileges"""
    try:
        return os.getuid() == 0
    except AttributeError:
        # Windows
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def get_python_executable():
    """Get the current Python executable path"""
    return sys.executable

def create_firewall_rule_powershell():
    """Create firewall rule using PowerShell"""
    print("🛡️  Creating Windows Firewall Rule")
    print("=" * 40)
    
    python_exe = get_python_executable()
    
    # PowerShell command to create firewall rule
    ps_commands = [
        # Remove existing rule if it exists
        'Remove-NetFirewallRule -DisplayName "ScratchV3-External-Access" -ErrorAction SilentlyContinue',
        
        # Create new inbound rule for port 8081
        'New-NetFirewallRule -DisplayName "ScratchV3-External-Access" -Direction Inbound -Protocol TCP -LocalPort 8081 -Action Allow -Profile Any -Description "Allow external access to ScratchV3 application"',
        
        # Create rule for Python executable
        f'New-NetFirewallRule -DisplayName "ScratchV3-Python" -Direction Inbound -Program "{python_exe}" -Action Allow -Profile Any -Description "Allow ScratchV3 Python application"'
    ]
    
    for i, cmd in enumerate(ps_commands, 1):
        print(f"Step {i}: {cmd.split()[0]}...")
        try:
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True, text=True, check=True
            )
            print(f"✅ Step {i} completed successfully")
        except subprocess.CalledProcessError as e:
            if "already exists" in e.stderr or "Remove-NetFirewallRule" in cmd:
                print(f"⚠️  Step {i}: Rule already exists or removed")
            else:
                print(f"❌ Step {i} failed: {e.stderr}")
                return False
        except Exception as e:
            print(f"❌ Step {i} error: {e}")
            return False
    
    return True

def verify_firewall_rules():
    """Verify that firewall rules were created"""
    print("\n🔍 Verifying Firewall Rules")
    print("=" * 30)
    
    try:
        # Check for ScratchV3 rules
        result = subprocess.run(
            ["powershell", "-Command", 'Get-NetFirewallRule -DisplayName "*ScratchV3*" | Select-Object DisplayName, Direction, Action, Enabled'],
            capture_output=True, text=True
        )
        
        if result.stdout.strip():
            print("✅ ScratchV3 firewall rules found:")
            print(result.stdout)
            return True
        else:
            print("❌ No ScratchV3 firewall rules found")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying rules: {e}")
        return False

def provide_manual_instructions():
    """Provide manual firewall configuration instructions"""
    print("\n📋 Manual Firewall Configuration")
    print("=" * 40)
    
    python_exe = get_python_executable()
    
    print("🔧 If automatic configuration failed, follow these steps:")
    print("\n1️⃣  Open Windows Defender Firewall with Advanced Security:")
    print("   • Press Win+R, type: wf.msc")
    print("   • Or search 'Windows Defender Firewall with Advanced Security'")
    
    print("\n2️⃣  Create Inbound Rule for Port 8081:")
    print("   • Click 'Inbound Rules' → 'New Rule'")
    print("   • Select 'Port' → Next")
    print("   • Select 'TCP' → Specific local ports: 8081")
    print("   • Select 'Allow the connection' → Next")
    print("   • Check all profiles (Domain, Private, Public) → Next")
    print("   • Name: 'ScratchV3-External-Access'")
    print("   • Description: 'Allow external access to ScratchV3'")
    
    print("\n3️⃣  Create Inbound Rule for Python:")
    print("   • Click 'Inbound Rules' → 'New Rule'")
    print("   • Select 'Program' → Next")
    print(f"   • Browse to: {python_exe}")
    print("   • Select 'Allow the connection' → Next")
    print("   • Check all profiles → Next")
    print("   • Name: 'ScratchV3-Python'")

def test_firewall_configuration():
    """Test firewall configuration"""
    print("\n🧪 Testing Firewall Configuration")
    print("=" * 35)
    
    print("📱 Local Tests:")
    print("   • Application should still work on https://192.168.1.4:8081")
    print("   • No connection blocking from Windows Firewall")
    
    print("\n🌐 External Tests (after router configuration):")
    print("   • External connections should reach the application")
    print("   • Port 8081 should be accessible from router port 8442")
    
    print("\n🔍 Verification Commands:")
    print("   • Check rules: Get-NetFirewallRule -DisplayName '*ScratchV3*'")
    print("   • Test port: Test-NetConnection -ComputerName localhost -Port 8081")

def provide_security_recommendations():
    """Provide security recommendations"""
    print("\n🛡️  Security Recommendations")
    print("=" * 35)
    
    print("✅ Current Configuration:")
    print("   • Port 8081 allowed for ScratchV3 application")
    print("   • Python executable allowed through firewall")
    print("   • Rules apply to all network profiles")
    
    print("\n⚠️  Additional Security Measures:")
    print("   • Monitor firewall logs regularly")
    print("   • Use strong authentication in ScratchV3")
    print("   • Consider IP whitelisting for known clients")
    print("   • Enable Windows Defender or third-party antivirus")
    print("   • Keep Windows and Python updated")
    
    print("\n🔒 Advanced Security (Optional):")
    print("   • Configure fail2ban equivalent for Windows")
    print("   • Use VPN instead of direct port forwarding")
    print("   • Implement rate limiting in application")
    print("   • Set up intrusion detection system")

def create_firewall_test_script():
    """Create a script to test firewall configuration"""
    script_content = '''#!/usr/bin/env python3
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
'''
    
    with open('scripts/test_firewall_config.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("\n📝 Created test script: scripts/test_firewall_config.py")

def main():
    """Main function"""
    print("🛡️  Windows Firewall Configuration for ScratchV3")
    print("=" * 50)
    
    # Check admin privileges
    if not check_admin_privileges():
        print("⚠️  Administrator privileges required for automatic configuration")
        print("   Please run as administrator or use manual instructions below")
        provide_manual_instructions()
        provide_security_recommendations()
        create_firewall_test_script()
        return
    
    # Create firewall rules
    success = create_firewall_rule_powershell()
    
    if success:
        # Verify rules
        verify_firewall_rules()
        print("\n✅ Windows Firewall configured successfully!")
    else:
        print("\n❌ Automatic configuration failed")
        provide_manual_instructions()
    
    # Provide additional information
    test_firewall_configuration()
    provide_security_recommendations()
    create_firewall_test_script()
    
    print("\n" + "=" * 50)
    print("📋 FIREWALL CONFIGURATION SUMMARY")
    print("=" * 50)
    print("✅ Port 8081 allowed for inbound connections")
    print("✅ Python executable allowed through firewall")
    print("✅ Rules apply to all network profiles")
    print("✅ ScratchV3 application can accept external connections")
    
    print("\n🎯 Next Steps:")
    print("1. Configure router port forwarding (8442 → 8081)")
    print("2. Update No-IP DNS configuration")
    print("3. Restart ScratchV3 application")
    print("4. Test external access")

if __name__ == "__main__":
    main()
