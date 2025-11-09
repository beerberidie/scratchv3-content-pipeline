#!/usr/bin/env python3
"""
Setup mkcert for trusted local SSL certificates
"""
import os
import subprocess
import sys
import platform

def install_mkcert():
    """Install mkcert based on the operating system"""
    system = platform.system().lower()
    
    print("🔧 Installing mkcert...")
    
    try:
        if system == "windows":
            # Check if Chocolatey is available
            subprocess.run(["choco", "--version"], check=True, capture_output=True)
            subprocess.run(["choco", "install", "mkcert", "-y"], check=True)
        elif system == "darwin":  # macOS
            # Check if Homebrew is available
            subprocess.run(["brew", "--version"], check=True, capture_output=True)
            subprocess.run(["brew", "install", "mkcert"], check=True)
        elif system == "linux":
            print("Please install mkcert manually:")
            print("curl -JLO 'https://dl.filippo.io/mkcert/latest?for=linux/amd64'")
            print("chmod +x mkcert-v*-linux-amd64")
            print("sudo cp mkcert-v*-linux-amd64 /usr/local/bin/mkcert")
            return False
        
        print("✅ mkcert installed successfully!")
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Failed to install mkcert automatically.")
        print("Please install mkcert manually from: https://github.com/FiloSottile/mkcert")
        return False
    except FileNotFoundError:
        print("❌ Package manager not found.")
        if system == "windows":
            print("Please install Chocolatey first: https://chocolatey.org/install")
        elif system == "darwin":
            print("Please install Homebrew first: https://brew.sh/")
        return False

def setup_mkcert_ca():
    """Setup mkcert CA"""
    try:
        print("🔐 Setting up mkcert CA...")
        subprocess.run(["mkcert", "-install"], check=True)
        print("✅ mkcert CA installed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error setting up mkcert CA: {e}")
        return False

def create_certificates():
    """Create certificates for local development"""
    ssl_dir = "ssl"
    os.makedirs(ssl_dir, exist_ok=True)
    
    cert_file = os.path.join(ssl_dir, "cert.pem")
    key_file = os.path.join(ssl_dir, "key.pem")
    
    try:
        print("🔐 Creating trusted SSL certificates...")
        subprocess.run([
            "mkcert", 
            "-cert-file", cert_file,
            "-key-file", key_file,
            "192.168.1.4", "localhost", "127.0.0.1"
        ], check=True)
        
        print("✅ SSL certificates created successfully!")
        print(f"   Certificate: {cert_file}")
        print(f"   Private Key: {key_file}")
        print("   These certificates are trusted by your system!")
        
        return cert_file, key_file
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating certificates: {e}")
        return None, None

if __name__ == "__main__":
    print("🚀 Setting up trusted SSL certificates with mkcert...")
    print()
    
    # Check if mkcert is already installed
    try:
        subprocess.run(["mkcert", "-version"], check=True, capture_output=True)
        print("✅ mkcert is already installed!")
    except (subprocess.CalledProcessError, FileNotFoundError):
        if not install_mkcert():
            sys.exit(1)
    
    # Setup CA
    if not setup_mkcert_ca():
        sys.exit(1)
    
    # Create certificates
    cert_file, key_file = create_certificates()
    
    if cert_file and key_file:
        print()
        print("🚀 To enable HTTPS, add these lines to your .env file:")
        print(f"USE_SSL=true")
        print(f"SSL_CERTFILE={cert_file}")
        print(f"SSL_KEYFILE={key_file}")
        print()
        print("Then restart your application and access:")
        print("https://192.168.1.4:8081")
