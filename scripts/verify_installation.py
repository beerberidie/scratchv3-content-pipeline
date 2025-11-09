#!/usr/bin/env python3
"""
ScratchV3 Installation Verification Script
Verifies that all dependencies are installed and the application is working correctly
"""
import subprocess
import sys
import requests
import urllib3
from pathlib import Path

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_virtual_environment():
    """Check if we're in a virtual environment"""
    print("🔍 Checking Virtual Environment")
    print("=" * 40)
    
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    venv_path = sys.prefix
    
    print(f"Virtual Environment: {'✅ Active' if in_venv else '❌ Not Active'}")
    print(f"Python Path: {sys.executable}")
    print(f"Environment Path: {venv_path}")
    
    return in_venv

def check_required_packages():
    """Check if all required packages are installed"""
    print("\n📦 Checking Required Packages")
    print("=" * 40)
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'pydantic-settings',
        'python-multipart',
        'httpx',
        'openai',
        'aiofiles',
        'jinja2',
        'email-validator',
        'apscheduler',
        'redis',
        'passlib',
        'python-jose',
        'aiosmtplib',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def check_ssl_configuration():
    """Check SSL certificate configuration"""
    print("\n🔐 Checking SSL Configuration")
    print("=" * 40)
    
    cert_file = Path("localhost+4.pem")
    key_file = Path("localhost+4-key.pem")
    env_file = Path(".env")
    
    print(f"Certificate File: {'✅' if cert_file.exists() else '❌'} {cert_file}")
    print(f"Private Key File: {'✅' if key_file.exists() else '❌'} {key_file}")
    print(f"Environment File: {'✅' if env_file.exists() else '❌'} {env_file}")
    
    # Check .env configuration
    ssl_configured = False
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'USE_SSL=true' in content and 'localhost+4.pem' in content:
                ssl_configured = True
    
    print(f"SSL Configuration: {'✅ Configured' if ssl_configured else '❌ Not Configured'}")
    
    return cert_file.exists() and key_file.exists() and ssl_configured

def test_application_endpoints():
    """Test application endpoints"""
    print("\n🧪 Testing Application Endpoints")
    print("=" * 40)
    
    endpoints = [
        "https://localhost:8081/health",
        "https://127.0.0.1:8081/health",
        "https://192.168.1.4:8081/health"
    ]
    
    results = []
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10, verify=False)
            if response.status_code == 200:
                print(f"✅ {endpoint} - Status: {response.status_code}")
                results.append(True)
            else:
                print(f"⚠️  {endpoint} - Status: {response.status_code}")
                results.append(False)
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} - Connection refused (app not running?)")
            results.append(False)
        except requests.exceptions.Timeout:
            print(f"❌ {endpoint} - Timeout")
            results.append(False)
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
            results.append(False)
    
    return all(results)

def check_application_startup():
    """Check if application can start without errors"""
    print("\n🚀 Checking Application Startup")
    print("=" * 40)
    
    try:
        # Try to import the main application
        from app.main import app
        print("✅ Application imports successfully")
        
        # Check if config loads
        from app.config import settings
        print("✅ Configuration loads successfully")
        print(f"   SSL Enabled: {settings.use_ssl}")
        print(f"   Certificate: {settings.ssl_certfile}")
        print(f"   Host: {settings.host}")
        print(f"   Port: {settings.port}")
        
        return True
        
    except Exception as e:
        print(f"❌ Application startup error: {e}")
        return False

def provide_next_steps():
    """Provide next steps for the user"""
    print("\n🎯 Next Steps")
    print("=" * 40)
    
    print("1. 🚀 Start the application:")
    print("   python run.py")
    
    print("\n2. 🌐 Access the application:")
    print("   • https://localhost:8081")
    print("   • https://127.0.0.1:8081")
    print("   • https://192.168.1.4:8081")
    
    print("\n3. 🔐 SSL Certificate Trust:")
    print("   • Certificates are created with mkcert (trusted by system)")
    print("   • If you see security warnings, clear browser cache")
    print("   • Try incognito/private browsing mode")
    
    print("\n4. 🛠️  If issues persist:")
    print("   • Check Windows Firewall for port 8081")
    print("   • Verify virtual environment is activated")
    print("   • Run: python scripts/browser_trust_setup.py")

def main():
    """Main verification function"""
    print("🔍 ScratchV3 Installation Verification")
    print("=" * 50)
    
    # Check virtual environment
    venv_ok = check_virtual_environment()
    
    # Check required packages
    packages_ok, missing = check_required_packages()
    
    # Check SSL configuration
    ssl_ok = check_ssl_configuration()
    
    # Check application startup
    startup_ok = check_application_startup()
    
    # Test endpoints (only if app is running)
    print("\n⚠️  Note: Endpoint tests require the application to be running")
    endpoints_ok = test_application_endpoints()
    
    # Summary
    print("\n📊 Verification Summary")
    print("=" * 50)
    print(f"Virtual Environment: {'✅' if venv_ok else '❌'}")
    print(f"Required Packages: {'✅' if packages_ok else '❌'}")
    print(f"SSL Configuration: {'✅' if ssl_ok else '❌'}")
    print(f"Application Startup: {'✅' if startup_ok else '❌'}")
    print(f"Endpoint Tests: {'✅' if endpoints_ok else '⚠️  (requires running app)'}")
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install " + " ".join(missing))
    
    overall_status = venv_ok and packages_ok and ssl_ok and startup_ok
    
    if overall_status:
        print("\n🎉 Installation Verification Complete!")
        print("✅ ScratchV3 is ready to run!")
    else:
        print("\n⚠️  Installation issues detected. Please fix the above issues.")
    
    # Provide next steps
    provide_next_steps()
    
    return overall_status

if __name__ == "__main__":
    main()
