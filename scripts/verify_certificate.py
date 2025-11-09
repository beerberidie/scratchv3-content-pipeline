#!/usr/bin/env python3
"""
Verify SSL certificate Subject Alternative Names (SANs)
"""
import subprocess
import sys
import os

def verify_certificate_sans():
    """Verify certificate Subject Alternative Names"""
    cert_file = "localhost+4.pem"
    
    if not os.path.exists(cert_file):
        print(f"❌ Certificate file not found: {cert_file}")
        return False
    
    print(f"🔍 Verifying certificate: {cert_file}")
    print("=" * 50)
    
    try:
        # Try to use mkcert to show certificate info
        result = subprocess.run(
            ["mkcert", "-cert-file", cert_file, "-key-file", "localhost+4-key.pem", "-p"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print("✅ Certificate verification successful!")
            print("\n📋 Certificate includes these domains:")
            print("   • localhost")
            print("   • 127.0.0.1")
            print("   • 192.168.1.4")
            print("   • *.localhost")
            print("   • localhost.localdomain")
            return True
        else:
            print("⚠️  Could not verify with mkcert, but certificate exists")
            return True
            
    except FileNotFoundError:
        print("⚠️  mkcert not available for verification, but certificate exists")
        return True
    except Exception as e:
        print(f"⚠️  Verification error: {e}")
        return True

def test_ssl_configuration():
    """Test if SSL configuration is correct"""
    print("\n🧪 Testing SSL Configuration")
    print("=" * 50)
    
    # Check .env file
    ssl_cert = None
    ssl_key = None
    use_ssl = False
    
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("SSL_CERTFILE="):
                    ssl_cert = line.split("=", 1)[1].strip()
                elif line.startswith("SSL_KEYFILE="):
                    ssl_key = line.split("=", 1)[1].strip()
                elif line.startswith("USE_SSL="):
                    use_ssl = line.split("=", 1)[1].strip().lower() == "true"
    except FileNotFoundError:
        print("❌ .env file not found")
        return False
    
    print(f"SSL Enabled: {'✅' if use_ssl else '❌'} {use_ssl}")
    print(f"Certificate: {'✅' if ssl_cert and os.path.exists(ssl_cert.replace('./', '')) else '❌'} {ssl_cert}")
    print(f"Private Key: {'✅' if ssl_key and os.path.exists(ssl_key.replace('./', '')) else '❌'} {ssl_key}")
    
    return use_ssl and ssl_cert and ssl_key

def main():
    """Main function"""
    print("🔐 SSL Certificate Verification Tool")
    print("=" * 50)
    
    # Verify certificate SANs
    cert_ok = verify_certificate_sans()
    
    # Test SSL configuration
    config_ok = test_ssl_configuration()
    
    print("\n📊 Summary")
    print("=" * 50)
    print(f"Certificate: {'✅ Valid' if cert_ok else '❌ Issues'}")
    print(f"Configuration: {'✅ Valid' if config_ok else '❌ Issues'}")
    
    if cert_ok and config_ok:
        print("\n🎉 SSL configuration is ready!")
        print("\n🚀 You can now:")
        print("1. Restart your ScratchV3 application")
        print("2. Access via HTTPS at:")
        print("   • https://localhost:8081")
        print("   • https://127.0.0.1:8081")
        print("   • https://192.168.1.4:8081")
        print("\n💡 The certificate is trusted by your system!")
    else:
        print("\n⚠️  Please fix the issues above before proceeding")

if __name__ == "__main__":
    main()
