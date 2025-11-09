#!/usr/bin/env python3
"""
Create a self-signed SSL certificate using Python's cryptography library
"""
import os
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import ipaddress

def create_ssl_certificate():
    """Create self-signed SSL certificate using cryptography library"""
    
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
    
    try:
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate subject
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ScratchApp"),
            x509.NameAttribute(NameOID.COMMON_NAME, "192.168.1.4"),
        ])
        
        # Create certificate
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
                x509.IPAddress(ipaddress.IPv4Address("192.168.1.4")),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write private key
        with open(key_file, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Write certificate
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        print("✅ SSL certificate created successfully!")
        print(f"   Certificate: {cert_file}")
        print(f"   Private Key: {key_file}")
        print()
        print("⚠️  Note: This is a self-signed certificate.")
        print("   Your browser will show a security warning.")
        print("   Click 'Advanced' and 'Proceed to 192.168.1.4' to continue.")
        
        return cert_file, key_file
        
    except Exception as e:
        print(f"❌ Error creating SSL certificate: {e}")
        return None, None

if __name__ == "__main__":
    cert_file, key_file = create_ssl_certificate()
    
    if cert_file and key_file:
        print()
        print("🚀 To enable HTTPS, update your .env file:")
        print("Uncomment these lines:")
        print("USE_SSL=true")
        print("SSL_CERTFILE=ssl/cert.pem")
        print("SSL_KEYFILE=ssl/key.pem")
        print()
        print("Then restart your application and access:")
        print("https://192.168.1.4:8081")
