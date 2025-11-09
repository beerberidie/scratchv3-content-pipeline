#!/usr/bin/env python3
"""
Setup Let's Encrypt SSL certificate for public hosting
"""
import os
import subprocess
import sys
import platform
import requests
import time

def check_domain_accessibility():
    """Check if the domain is accessible from the internet"""
    domain = "scratchgpt.webhop.me"
    port = "8442"
    
    print(f"🌐 Checking if {domain}:{port} is accessible from the internet...")
    
    try:
        # Try to access the domain from an external perspective
        response = requests.get(f"http://{domain}:{port}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Domain {domain}:{port} is accessible!")
            return True
        else:
            print(f"⚠️  Domain accessible but returned status {response.status_code}")
            return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Domain {domain}:{port} is not accessible from the internet")
        print(f"Error: {e}")
        return False

def install_certbot_windows():
    """Install Certbot on Windows"""
    print("🔧 Installing Certbot for Windows...")
    print("Please follow these steps:")
    print("1. Download Certbot from: https://dl.eff.org/certbot-beta-installer-win32.exe")
    print("2. Run the installer as Administrator")
    print("3. After installation, restart this script")
    print()
    input("Press Enter after installing Certbot...")
    
    # Check if certbot is now available
    try:
        subprocess.run(["certbot", "--version"], check=True, capture_output=True)
        print("✅ Certbot installed successfully!")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Certbot not found. Please install it manually.")
        return False

def check_certbot():
    """Check if Certbot is installed"""
    try:
        result = subprocess.run(["certbot", "--version"], check=True, capture_output=True, text=True)
        print(f"✅ Certbot found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Certbot not found")
        return False

def get_certificate_manual():
    """Get certificate using manual DNS verification"""
    domain = "scratchgpt.webhop.me"
    
    print(f"🔐 Getting SSL certificate for {domain}...")
    print("This will use DNS verification method.")
    print()
    
    cmd = [
        "certbot", "certonly",
        "--manual",
        "--preferred-challenges", "dns",
        "--email", "your-email@example.com",  # You'll need to change this
        "--agree-tos",
        "--no-eff-email",
        "-d", domain
    ]
    
    print("Running command:")
    print(" ".join(cmd))
    print()
    print("⚠️  IMPORTANT: You'll need to add a DNS TXT record when prompted!")
    print("Follow the instructions carefully.")
    print()
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Certificate obtained successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get certificate: {e}")
        return False

def setup_certificate_files():
    """Setup certificate files for the application"""
    cert_dir = "/etc/letsencrypt/live/scratchgpt.webhop.me"
    app_ssl_dir = "ssl"
    
    if platform.system() == "Windows":
        cert_dir = "C:\\Certbot\\live\\scratchgpt.webhop.me"
    
    if not os.path.exists(cert_dir):
        print(f"❌ Certificate directory not found: {cert_dir}")
        return False
    
    # Create ssl directory
    os.makedirs(app_ssl_dir, exist_ok=True)
    
    # Copy certificates
    try:
        import shutil
        shutil.copy(os.path.join(cert_dir, "fullchain.pem"), os.path.join(app_ssl_dir, "cert.pem"))
        shutil.copy(os.path.join(cert_dir, "privkey.pem"), os.path.join(app_ssl_dir, "key.pem"))
        
        print("✅ Certificates copied to ssl/ directory")
        return True
    except Exception as e:
        print(f"❌ Failed to copy certificates: {e}")
        return False

def main():
    print("🔐 Let's Encrypt SSL Certificate Setup")
    print("=" * 50)
    
    # Check domain accessibility
    if not check_domain_accessibility():
        print()
        print("⚠️  Your domain is not accessible from the internet.")
        print("This might be because:")
        print("1. No-IP forwarding is not set up correctly")
        print("2. Your router/firewall is blocking the connection")
        print("3. The port forwarding is not configured")
        print()
        print("Please fix the domain accessibility first, then run this script again.")
        return
    
    # Check if Certbot is installed
    if not check_certbot():
        if platform.system() == "Windows":
            if not install_certbot_windows():
                return
        else:
            print("Please install Certbot:")
            print("Ubuntu/Debian: sudo apt-get install certbot")
            print("CentOS/RHEL: sudo yum install certbot")
            print("macOS: brew install certbot")
            return
    
    # Get certificate
    print()
    print("🔐 Getting SSL certificate...")
    print("You have two options:")
    print("1. Manual DNS verification (recommended for No-IP)")
    print("2. HTTP verification (requires port 80 access)")
    print()
    
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == "1":
        if get_certificate_manual():
            setup_certificate_files()
    else:
        print("HTTP verification not implemented yet.")
        print("Please use option 1 (DNS verification).")
    
    print()
    print("📋 Next steps:")
    print("1. Update your .env file to use the new certificates")
    print("2. Restart your application")
    print("3. Test HTTPS access")

if __name__ == "__main__":
    main()
