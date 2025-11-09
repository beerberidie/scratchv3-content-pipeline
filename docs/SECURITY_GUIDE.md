# 🔒 ScratchV3 Security Guide

Comprehensive security checklist and hardening guide for production deployment.

## 🛡️ Security Overview

ScratchV3 handles sensitive data including:
- API keys for AI services
- WordPress credentials
- User authentication sessions
- Generated content and chat references
- Task scheduling and automation

## 🔐 Authentication & Authorization

### Session Security
```bash
# Production session configuration
SESSION_SECURE=true          # HTTPS-only cookies
SESSION_EXPIRE_HOURS=24      # Session timeout
SECRET_KEY=<strong-key>      # 32+ character random key
```

### User Management
- **Static user list** - No dynamic user registration
- **Strong passwords** - Minimum 12 characters with complexity
- **Session timeout** - Automatic logout after inactivity
- **Login rate limiting** - Prevent brute force attacks

### API Security
- **Authentication required** - All endpoints except login require valid session
- **CSRF protection** - Built-in FastAPI CSRF protection
- **Input validation** - Pydantic models validate all inputs
- **Rate limiting** - Per-user request limits

## 🔑 API Key Management

### Encryption at Rest
```python
# API keys are encrypted using Fernet (AES 128)
ENCRYPTION_KEY=<32-byte-key>  # Generate with Fernet.generate_key()
```

### Key Storage Security
- **Encrypted storage** - All API keys encrypted before storage
- **Separate key files** - Keys stored per user in isolated files
- **No plaintext logging** - Keys never logged in plaintext
- **Secure transmission** - HTTPS required for key updates

### Key Validation
- **Real-time validation** - Keys tested against provider APIs
- **Status monitoring** - Invalid keys flagged immediately
- **Automatic cleanup** - Failed keys can be removed

## 🌐 Network Security

### HTTPS Configuration
```nginx
# Force HTTPS redirect
server {
    listen 80;
    return 301 https://$server_name$request_uri;
}

# Strong SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;
```

### Security Headers
```bash
# Enable security headers
ENABLE_SECURITY_HEADERS=true
```

Headers implemented:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Referrer-Policy: strict-origin-when-cross-origin`

### Rate Limiting
```bash
# Configure rate limits
RATE_LIMIT_PER_MINUTE=100    # Requests per minute
RATE_LIMIT_PER_HOUR=1000     # Requests per hour
RATE_LIMIT_BURST=20          # Burst allowance
```

## 📁 File Security

### Upload Restrictions
```bash
# File upload security
MAX_UPLOAD_SIZE=10485760     # 10MB limit
ALLOWED_EXTENSIONS=txt,md,json
UPLOAD_DIR=./uploads         # Isolated directory
```

### File Validation
- **Extension whitelist** - Only allowed file types
- **Size limits** - Prevent large file attacks
- **Content scanning** - Basic content validation
- **Isolated storage** - Uploads stored outside web root

### Directory Permissions
```bash
# Secure file permissions
chmod 755 data/ uploads/     # Directory access
chmod 644 data/*/*.json      # File read/write
chmod 600 .env               # Environment file
```

## 🗄️ Database Security

### Connection Security
```bash
# Secure database connection
DATABASE_URL=postgresql://user:pass@localhost:5432/db?sslmode=require
```

### Data Protection
- **Encrypted sensitive fields** - API keys and passwords encrypted
- **Input sanitization** - All inputs validated and sanitized
- **Parameterized queries** - No SQL injection vulnerabilities
- **Regular backups** - Encrypted backup storage

### Access Control
- **Dedicated database user** - Limited privileges
- **Network isolation** - Database not exposed to internet
- **Connection pooling** - Controlled connection limits

## 🔄 Redis Security

### Configuration
```bash
# Redis security settings
REDIS_URL=redis://:password@localhost:6379/0
```

### Security Measures
- **Password protection** - Redis AUTH enabled
- **Network binding** - Bind to localhost only
- **Command restrictions** - Disable dangerous commands
- **Regular cleanup** - Automatic key expiration

## 🚨 Monitoring & Logging

### Security Logging
```bash
# Logging configuration
LOG_LEVEL=WARNING            # Production log level
LOG_REQUESTS=false           # Disable request logging
```

### Monitored Events
- Failed login attempts
- API key validation failures
- Rate limit violations
- File upload attempts
- Database connection errors
- Redis connection failures

### Log Security
- **No sensitive data** - API keys and passwords never logged
- **Log rotation** - Automatic log cleanup
- **Secure storage** - Logs stored with restricted access
- **Monitoring alerts** - Automated security alerts

## 🛠️ Production Hardening

### Environment Configuration
```bash
# Production security settings
ENVIRONMENT=production
DEBUG=false
FORCE_HTTPS=true
SESSION_SECURE=true
ENABLE_SECURITY_HEADERS=true
TRUST_PROXY_HEADERS=true
```

### System Hardening
- **Firewall configuration** - Only necessary ports open
- **Service isolation** - Run as non-root user
- **Regular updates** - Keep system and dependencies updated
- **Backup encryption** - Encrypted backup storage

### Application Security
- **Error handling** - No sensitive data in error messages
- **Input validation** - Comprehensive input sanitization
- **Output encoding** - Prevent XSS attacks
- **CSRF protection** - Cross-site request forgery prevention

## 🔍 Security Testing

### Automated Testing
```bash
# Security test commands
pytest tests/security/
bandit -r app/
safety check
```

### Manual Testing
- **Authentication bypass** - Test session handling
- **Input validation** - Test with malicious inputs
- **File upload** - Test with various file types
- **Rate limiting** - Test limit enforcement
- **HTTPS enforcement** - Verify redirect behavior

### Penetration Testing
- **OWASP Top 10** - Test against common vulnerabilities
- **API security** - Test endpoint security
- **Session management** - Test session handling
- **Input validation** - Test injection attacks

## 📋 Security Checklist

### Pre-Deployment Security
- [ ] Strong `SECRET_KEY` and `ENCRYPTION_KEY` generated
- [ ] `DEBUG=false` in production
- [ ] HTTPS enforced (`FORCE_HTTPS=true`)
- [ ] Security headers enabled
- [ ] Rate limiting configured
- [ ] File upload restrictions in place
- [ ] Database credentials secured
- [ ] Redis password configured
- [ ] Firewall rules configured
- [ ] SSL certificate installed and valid

### API Key Security
- [ ] Encryption key generated and secured
- [ ] API keys encrypted at rest
- [ ] Key validation working
- [ ] No keys in logs or error messages
- [ ] Key rotation process documented
- [ ] Invalid key cleanup implemented

### Authentication Security
- [ ] Strong password policy enforced
- [ ] Session timeout configured
- [ ] Login rate limiting active
- [ ] CSRF protection enabled
- [ ] Session cookies secure (HTTPS-only)
- [ ] No default credentials in use

### File & Data Security
- [ ] File upload restrictions enforced
- [ ] Directory permissions set correctly
- [ ] Database access restricted
- [ ] Sensitive data encrypted
- [ ] Backup encryption enabled
- [ ] Log files secured

### Network Security
- [ ] HTTPS certificate valid
- [ ] Strong SSL/TLS configuration
- [ ] Security headers implemented
- [ ] Unnecessary ports closed
- [ ] Network segmentation in place
- [ ] DDoS protection configured

### Monitoring & Incident Response
- [ ] Security logging enabled
- [ ] Log monitoring configured
- [ ] Incident response plan documented
- [ ] Security contact information updated
- [ ] Backup and recovery tested
- [ ] Security update process established

## 🚨 Incident Response

### Security Incident Types
1. **Unauthorized access** - Failed login attempts, session hijacking
2. **Data breach** - Exposed API keys, user data
3. **Service disruption** - DDoS attacks, resource exhaustion
4. **Malware/injection** - Code injection, file uploads

### Response Procedures
1. **Immediate containment** - Isolate affected systems
2. **Assessment** - Determine scope and impact
3. **Notification** - Alert stakeholders and users
4. **Recovery** - Restore services and data
5. **Post-incident** - Review and improve security

### Emergency Contacts
- System Administrator: [contact info]
- Security Team: [contact info]
- Hosting Provider: [contact info]
- Legal/Compliance: [contact info]

## 🔄 Security Maintenance

### Regular Tasks
- **Weekly**: Review security logs and alerts
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Security assessment and penetration testing
- **Annually**: Full security audit and policy review

### Security Updates
- **Dependency updates** - Regular security patch application
- **Configuration review** - Periodic security setting review
- **Access review** - Regular user access audit
- **Backup testing** - Regular backup and recovery testing

### Compliance
- **Data protection** - GDPR/CCPA compliance if applicable
- **Industry standards** - Follow relevant security frameworks
- **Documentation** - Maintain security documentation
- **Training** - Regular security awareness training
