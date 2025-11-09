# Scripts Directory

This directory contains utility scripts, tools, and standalone test files for the ScratchV3 project.

## Directory Structure

### `/debug/`
Debug and diagnostic scripts:
- `check_settings.py` - Verify application settings
- `debug_lmstudio_request.py` - Debug LM Studio API requests
- `validate_lmstudio_integration.py` - Validate LM Studio integration
- `verify_wordpress_fix.py` - Verify WordPress functionality

### `/setup/`
Installation and setup scripts:
- `create_ssl_cert.py` - Create SSL certificates
- `create_ssl_cert_python.py` - Alternative SSL certificate creation
- `generate_secrets.py` - Generate application secrets
- `install_redis.bat` - Install Redis on Windows
- `setup_letsencrypt.py` - Setup Let's Encrypt certificates
- `setup_mkcert.py` - Setup mkcert for local development
- `ssl_alternatives.py` - Alternative SSL setup methods

### `/tests/`
Standalone test scripts and test HTML files:
- `test_*.py` - Various standalone test scripts
- `test_*.html` - Test HTML files for UI testing

### Root Scripts
General utility scripts:
- `fix_lmstudio_settings.py` - Fix LM Studio configuration
- `migrate_task_data.py` - Migrate task data between versions
- `public_hosting_security.py` - Security setup for public hosting
- `security_hardening.py` - General security hardening

## Usage

Run scripts from the project root directory:

```bash
# Debug scripts
python scripts/debug/check_settings.py

# Setup scripts
python scripts/setup/generate_secrets.py

# Test scripts
python scripts/tests/test_fix_simple.py

# Utility scripts
python scripts/migrate_task_data.py
```

## Note

Most scripts expect to be run from the project root directory to properly access the `app` module and configuration files.
