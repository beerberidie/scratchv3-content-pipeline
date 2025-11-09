#!/usr/bin/env python3
"""
Security hardening checklist and automated fixes
"""
import os
import stat
import subprocess
import sys

def check_file_permissions():
    """Check and fix file permissions"""
    print("🔒 Checking file permissions...")
    
    # Check .env file permissions
    if os.path.exists('.env'):
        current_perms = oct(os.stat('.env').st_mode)[-3:]
        if current_perms != '600':
            print(f"⚠️  .env file permissions: {current_perms} (should be 600)")
            try:
                os.chmod('.env', stat.S_IRUSR | stat.S_IWUSR)
                print("✅ Fixed .env permissions to 600")
            except Exception as e:
                print(f"❌ Failed to fix .env permissions: {e}")
        else:
            print("✅ .env file permissions are secure")
    
    # Check data directory permissions
    if os.path.exists('data'):
        print("✅ Data directory exists")
        # Set secure permissions for data files
        for root, dirs, files in os.walk('data'):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)
                except Exception as e:
                    print(f"⚠️  Could not secure {filepath}: {e}")

def check_environment_config():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    with open('.env', 'r') as f:
        env_content = f.read()
    
    issues = []
    
    # Check for default secret key
    if 'SECRET_KEY=change-me-in-production' in env_content:
        issues.append("Default SECRET_KEY detected")
    
    # Check for debug mode
    if 'DEBUG=True' in env_content or 'DEBUG=true' in env_content:
        issues.append("Debug mode is enabled")
    
    # Check for missing encryption key
    if 'ENCRYPTION_KEY=' not in env_content:
        issues.append("ENCRYPTION_KEY not set")
    
    # Check for SSL configuration
    if 'USE_SSL=true' not in env_content:
        issues.append("SSL not enabled")
    
    if issues:
        print("❌ Environment configuration issues:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ Environment configuration looks good")
        return True

def check_ssl_certificates():
    """Check SSL certificate configuration"""
    print("\n🔐 Checking SSL certificates...")
    
    if not os.path.exists('ssl/cert.pem') or not os.path.exists('ssl/key.pem'):
        print("❌ SSL certificates not found")
        return False
    
    # Check certificate validity (basic check)
    try:
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend
        
        with open('ssl/cert.pem', 'rb') as f:
            cert = x509.load_pem_x509_certificate(f.read(), default_backend())
        
        # Check if certificate is expired
        from datetime import datetime
        if cert.not_valid_after < datetime.utcnow():
            print("❌ SSL certificate has expired")
            return False
        
        print("✅ SSL certificates are valid")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not validate SSL certificates: {e}")
        return False

def check_dependencies():
    """Check for security vulnerabilities in dependencies"""
    print("\n📦 Checking dependencies for security vulnerabilities...")
    
    try:
        # Run safety check if available
        result = subprocess.run(['safety', 'check'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ No known security vulnerabilities found")
            return True
        else:
            print("❌ Security vulnerabilities found:")
            print(result.stdout)
            return False
    except FileNotFoundError:
        print("⚠️  'safety' tool not installed. Run: pip install safety")
        return None

def generate_security_report():
    """Generate a comprehensive security report"""
    print("\n📋 Security Assessment Report")
    print("=" * 50)
    
    checks = [
        ("File Permissions", check_file_permissions),
        ("Environment Config", check_environment_config),
        ("SSL Certificates", check_ssl_certificates),
        ("Dependencies", check_dependencies)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            results[name] = False
    
    print("\n📊 Summary:")
    all_good = True
    for name, result in results.items():
        if result is True:
            print(f"✅ {name}: PASS")
        elif result is False:
            print(f"❌ {name}: FAIL")
            all_good = False
        else:
            print(f"⚠️  {name}: WARNING")
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All security checks passed!")
        print("Your application is ready for hosting.")
    else:
        print("⚠️  Security issues found.")
        print("Please address the issues above before hosting.")
    
    return all_good

if __name__ == "__main__":
    print("🛡️  Security Hardening Tool")
    print("Checking your application for security issues...\n")
    
    is_secure = generate_security_report()
    
    if not is_secure:
        print("\n🔧 Quick fixes:")
        print("1. Run: python generate_secrets.py")
        print("2. Update your .env file with the generated keys")
        print("3. Set DEBUG=False in .env")
        print("4. Ensure SSL certificates are valid")
        print("5. Run: pip install safety && safety check")
        
        sys.exit(1)
    else:
        sys.exit(0)
