#!/usr/bin/env python3
"""
Create a self-signed SSL certificate for local development
"""
import os
import subprocess
import sys

def create_ssl_certificate():
    """Create self-signed SSL certificate"""
    
    # Create ssl directory if it doesn't exist
    ssl_dir = "ssl"
    os.makedirs(ssl_dir, exist_ok=True)
    
    cert_file = os.path.join(ssl_dir, "cert.pem")
    key_file = os.path.join(ssl_dir, "key.pem")
    
    # Check if certificates already exist
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("✅ SSL certificates already exist!")
        print(f"   Certificate: {cert_file}")
        print(f"   Private Key: {key_file}")
        return cert_file, key_file
    
    print("🔐 Creating self-signed SSL certificate...")
    
    # Create self-signed certificate
    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096", 
        "-keyout", key_file, "-out", cert_file,
        "-days", "365", "-nodes",
        "-subj", "/C=US/ST=Local/L=Local/O=ScratchApp/CN=192.168.1.4"
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print("✅ SSL certificate created successfully!")
        print(f"   Certificate: {cert_file}")
        print(f"   Private Key: {key_file}")
        print()
        print("⚠️  Note: This is a self-signed certificate.")
        print("   Your browser will show a security warning.")
        print("   Click 'Advanced' and 'Proceed to 192.168.1.4' to continue.")
        
        return cert_file, key_file
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating SSL certificate: {e}")
        print("Make sure OpenSSL is installed on your system.")
        return None, None
    except FileNotFoundError:
        print("❌ OpenSSL not found. Please install OpenSSL:")
        print("   Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        print("   macOS: brew install openssl")
        print("   Linux: sudo apt-get install openssl")
        return None, None

if __name__ == "__main__":
    cert_file, key_file = create_ssl_certificate()
    
    if cert_file and key_file:
        print()
        print("🚀 To enable HTTPS, add these lines to your .env file:")
        print(f"USE_SSL=true")
        print(f"SSL_CERTFILE={cert_file}")
        print(f"SSL_KEYFILE={key_file}")
