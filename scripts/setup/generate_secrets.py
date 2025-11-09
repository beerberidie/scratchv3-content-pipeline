#!/usr/bin/env python3
"""
Generate secure secret keys for production deployment
"""
import secrets
import string
from cryptography.fernet import Fernet

def generate_secret_key(length=64):
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_encryption_key():
    """Generate a Fernet encryption key"""
    return Fernet.generate_key().decode()

if __name__ == "__main__":
    print("🔐 Generating secure keys for production...")
    print()
    
    secret_key = generate_secret_key()
    encryption_key = generate_encryption_key()
    
    print("Add these to your .env file:")
    print("=" * 50)
    print(f"SECRET_KEY={secret_key}")
    print(f"ENCRYPTION_KEY={encryption_key}")
    print("=" * 50)
    print()
    print("⚠️  IMPORTANT:")
    print("- Keep these keys secure and never share them")
    print("- Back up these keys safely")
    print("- If you lose these keys, all encrypted data will be unrecoverable")
    print("- Restart your application after updating .env")
