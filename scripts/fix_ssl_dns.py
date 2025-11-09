#!/usr/bin/env python3
"""
Fix SSL/DNS issues for ScratchV3 application
This script creates proper SSL certificates with all required SANs and fixes configuration
"""
import os
import subprocess
import sys
import platform
from pathlib import Path

def check_mkcert():
    """Check if mkcert is available"""
    try:
        result = subprocess.run(["mkcert", "-version"], capture_output=True, text=True)
        print("✅ mkcert is available")
        return True
    except FileNotFoundError:
        print("❌ mkcert not found")
        return False

def install_mkcert_windows():
    """Install mkcert on Windows"""
    print("📦 Installing mkcert...")
    
    # Check if Chocolatey is available
    try:
        subprocess.run(["choco", "--version"], capture_output=True, check=True)
        print("Installing mkcert via Chocolatey...")
        subprocess.run(["choco", "install", "mkcert", "-y"], check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    # Check if Scoop is available
    try:
        subprocess.run(["scoop", "--version"], capture_output=True, check=True)
        print("Installing mkcert via Scoop...")
        subprocess.run(["scoop", "install", "mkcert"], check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    print("❌ Please install mkcert manually:")
    print("   1. Download from: https://github.com/FiloSottile/mkcert/releases")
    print("   2. Or install Chocolatey/Scoop first")
    return False

def setup_mkcert_ca():
    """Setup mkcert CA"""
    try:
        print("🔐 Setting up mkcert CA...")
        subprocess.run(["mkcert", "-install"], check=True)
        print("✅ mkcert CA installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to setup mkcert CA: {e}")
        return False

def create_comprehensive_certificate():
    """Create SSL certificate with all required SANs"""
    print("🔐 Creating comprehensive SSL certificate...")
    
    # Define all possible access points
    domains = [
        "localhost",
        "127.0.0.1", 
        "192.168.1.4",
        "*.localhost",
        "localhost.localdomain"
    ]
    
    # Create certificate with all domains
    cmd = ["mkcert"] + domains
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ SSL certificate created successfully!")
        
        # Find the generated files
        cert_files = []
        for file in os.listdir("."):
            if file.endswith(".pem") and "localhost" in file:
                cert_files.append(file)
        
        if len(cert_files) >= 2:
            # Find cert and key files
            cert_file = None
            key_file = None
            
            for file in cert_files:
                if "key" in file:
                    key_file = file
                else:
                    cert_file = file
            
            if cert_file and key_file:
                print(f"   Certificate: {cert_file}")
                print(f"   Private Key: {key_file}")
                return cert_file, key_file
        
        print("❌ Could not identify certificate files")
        return None, None
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating certificate: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")
        return None, None

def update_env_file(cert_file, key_file):
    """Update .env file with correct certificate paths"""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print("❌ .env file not found")
        return False
    
    # Read current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update SSL configuration lines
    updated_lines = []
    for line in lines:
        if line.startswith("SSL_CERTFILE="):
            updated_lines.append(f"SSL_CERTFILE=./{cert_file}\n")
        elif line.startswith("SSL_KEYFILE="):
            updated_lines.append(f"SSL_KEYFILE=./{key_file}\n")
        else:
            updated_lines.append(line)
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print("✅ .env file updated with new certificate paths")
    return True

def test_certificate_access():
    """Test certificate access"""
    print("\n🧪 Testing certificate configuration...")
    
    # Test if certificate files are readable
    env_vars = {}
    with open(".env", 'r') as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                env_vars[key] = value
    
    cert_file = env_vars.get("SSL_CERTFILE", "").replace("./", "")
    key_file = env_vars.get("SSL_KEYFILE", "").replace("./", "")
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"✅ Certificate files accessible:")
        print(f"   Cert: {cert_file}")
        print(f"   Key: {key_file}")
        return True
    else:
        print(f"❌ Certificate files not found:")
        print(f"   Cert: {cert_file} (exists: {os.path.exists(cert_file)})")
        print(f"   Key: {key_file} (exists: {os.path.exists(key_file)})")
        return False

def main():
    """Main function"""
    print("🚀 ScratchV3 SSL/DNS Fix Tool")
    print("=" * 50)
    
    # Check if mkcert is available
    if not check_mkcert():
        if platform.system() == "Windows":
            if not install_mkcert_windows():
                sys.exit(1)
        else:
            print("Please install mkcert:")
            print("  macOS: brew install mkcert")
            print("  Linux: See https://github.com/FiloSottile/mkcert#installation")
            sys.exit(1)
    
    # Setup mkcert CA
    if not setup_mkcert_ca():
        sys.exit(1)
    
    # Create comprehensive certificate
    cert_file, key_file = create_comprehensive_certificate()
    if not cert_file or not key_file:
        sys.exit(1)
    
    # Update .env file
    if not update_env_file(cert_file, key_file):
        sys.exit(1)
    
    # Test configuration
    if not test_certificate_access():
        sys.exit(1)
    
    print("\n🎉 SSL/DNS Fix Complete!")
    print("=" * 50)
    print("✅ Trusted SSL certificate created")
    print("✅ .env file updated")
    print("✅ Certificate files verified")
    print()
    print("🚀 Next steps:")
    print("1. Restart your ScratchV3 application")
    print("2. Access via:")
    print("   • https://localhost:8081")
    print("   • https://127.0.0.1:8081")
    print("   • https://192.168.1.4:8081")
    print()
    print("⚠️  If you still get DNS errors:")
    print("1. Clear browser cache and cookies")
    print("2. Try incognito/private browsing mode")
    print("3. Check Windows Firewall settings")

if __name__ == "__main__":
    main()
