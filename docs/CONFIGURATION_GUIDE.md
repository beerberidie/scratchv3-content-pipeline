# ⚙️ ScratchV3 Configuration Guide

Complete guide for configuring ScratchV3 for different environments and use cases.

## 🚀 Quick Setup

### 1. Environment File Setup
```bash
# Copy the example environment file
cp .env.example .env

# Edit with your specific configuration
nano .env  # or your preferred editor
```

### 2. Required Configuration
At minimum, you need to configure:
- `SECRET_KEY` - Application security
- `ENCRYPTION_KEY` - For encrypting sensitive data
- At least one AI provider (OpenAI or OpenRouter)
- Redis connection

### 3. Generate Security Keys
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## 🔑 API Key Configuration

### OpenAI Setup
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add to `.env`:
   ```bash
   OPENAI_API_KEY=sk-your-openai-key-here
   ```

### OpenRouter Setup (Alternative)
1. Visit [OpenRouter](https://openrouter.ai/keys)
2. Create account and generate API key
3. Add to `.env`:
   ```bash
   OPENROUTER_API_KEY=sk-or-your-openrouter-key-here
   ```

### Pexels Setup (Optional)
1. Visit [Pexels API](https://www.pexels.com/api/)
2. Create account and get API key
3. Add to `.env`:
   ```bash
   PEXELS_API_KEY=your-pexels-api-key-here
   ```

## 🗄️ Database Configuration

### SQLite (Default - Development)
```bash
DATABASE_URL=sqlite:///./data/app.db
```
- No additional setup required
- Good for development and small deployments
- Data stored in `./data/app.db`

### PostgreSQL (Recommended - Production)
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib  # Ubuntu/Debian
brew install postgresql  # macOS

# Create database
sudo -u postgres createdb scratchv3

# Configure connection
DATABASE_URL=postgresql://username:password@localhost:5432/scratchv3
```

### MySQL (Alternative)
```bash
# Install MySQL
sudo apt-get install mysql-server  # Ubuntu/Debian
brew install mysql  # macOS

# Create database
mysql -u root -p -e "CREATE DATABASE scratchv3;"

# Configure connection
DATABASE_URL=mysql://username:password@localhost:3306/scratchv3
```

## 🔄 Redis Configuration

### Local Redis
```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis  # macOS

# Start Redis
sudo systemctl start redis-server  # Ubuntu/Debian
brew services start redis  # macOS

# Configure in .env
REDIS_URL=redis://localhost:6379/0
```

### Redis with Authentication
```bash
REDIS_URL=redis://:password@localhost:6379/0
```

### Redis Cloud/Cluster
```bash
REDIS_URL=redis://user:password@redis-cluster.example.com:6379/0
```

## 🌍 Environment-Specific Configuration

### Development Environment
```bash
# .env for development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
AUTO_RELOAD=true
ENABLE_CORS=true
SESSION_SECURE=false
FORCE_HTTPS=false
```

### Staging Environment
```bash
# .env for staging
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
AUTO_RELOAD=false
ENABLE_CORS=false
SESSION_SECURE=true
FORCE_HTTPS=true
```

### Production Environment
```bash
# .env for production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
AUTO_RELOAD=false
ENABLE_CORS=false
SESSION_SECURE=true
FORCE_HTTPS=true
ENABLE_SECURITY_HEADERS=true
TRUST_PROXY_HEADERS=true
```

## 🔒 Security Configuration

### Essential Security Settings
```bash
# Strong secret keys
SECRET_KEY=your-strong-secret-key-here
ENCRYPTION_KEY=your-32-byte-encryption-key-here

# Session security
SESSION_EXPIRE_HOURS=24
SESSION_SECURE=true  # Only with HTTPS

# HTTPS enforcement
FORCE_HTTPS=true

# Security headers
ENABLE_SECURITY_HEADERS=true
```

### Rate Limiting
```bash
# Adjust based on your needs
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_BURST=20
```

### File Upload Security
```bash
# Limit file sizes and types
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=txt,md,json
UPLOAD_DIR=./uploads
```

## 🤖 AI Configuration

### Model Selection
```bash
# Primary AI model
DEFAULT_AI_MODEL=gpt-4

# Response limits
MAX_RESPONSE_TOKENS=2000
MIN_WORD_COUNT=100
MAX_WORD_COUNT=3000
```

### Content Quality
```bash
# Enable quality filtering
ENABLE_QA_FILTER=true

# Advanced AI features
ENABLE_ADVANCED_AI=true
```

## 📊 Monitoring & Logging

### Basic Logging
```bash
# Log level
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Log to file (optional)
LOG_FILE=./logs/app.log

# Request logging
LOG_REQUESTS=false  # Enable for debugging
```

### Health Checks
```bash
# Health check configuration
HEALTH_CHECK_TIMEOUT=5
DETAILED_HEALTH_CHECKS=true
```

### External Monitoring
```bash
# Sentry for error tracking
SENTRY_DSN=https://your-sentry-dsn-here

# Application Insights
APPINSIGHTS_INSTRUMENTATION_KEY=your-key-here
```

## 🌐 WordPress Configuration

### WordPress Settings
```bash
# WordPress integration
ENABLE_WORDPRESS=true
WP_TIMEOUT=30
WP_API_VERSION=wp/v2
```

### WordPress Sites
WordPress sites are configured through the web interface:
1. Navigate to Settings → WordPress
2. Add your WordPress site URLs
3. Configure credentials (stored encrypted)

## 🔧 Performance Tuning

### Task Processing
```bash
# Concurrent task limits
MAX_CONCURRENT_TASKS=5
TASK_TIMEOUT=300

# Retry configuration
MAX_RETRIES=3
RETRY_DELAY=60
```

### External API Settings
```bash
# API timeouts
EXTERNAL_API_TIMEOUT=30
EXTERNAL_API_RETRIES=3
USER_AGENT=ScratchV3/1.0
```

## 🐳 Docker Configuration

### Docker Environment
```bash
# Docker-specific settings
HOST=0.0.0.0
PORT=8000
TRUST_PROXY_HEADERS=true

# Use environment-specific database
DATABASE_URL=postgresql://postgres:password@db:5432/scratchv3
REDIS_URL=redis://redis:6379/0
```

### Docker Compose Example
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/scratchv3
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: scratchv3
      POSTGRES_PASSWORD: password
  
  redis:
    image: redis:6-alpine
```

## 🔍 Troubleshooting

### Common Issues

**Redis Connection Failed**
```bash
# Check Redis status
redis-cli ping

# Verify Redis URL
REDIS_URL=redis://localhost:6379/0
```

**Database Connection Issues**
```bash
# Test database connection
python -c "from app.config import get_settings; print(get_settings().database_url)"

# Run migrations
alembic upgrade head
```

**API Key Validation Errors**
```bash
# Test API keys through the web interface
# Settings → API Keys → Check status

# Or test manually
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

**Permission Errors**
```bash
# Ensure proper file permissions
chmod 755 ./data
chmod 755 ./uploads
chmod 644 .env
```

### Debug Mode
```bash
# Enable debug mode for troubleshooting
DEBUG=true
LOG_LEVEL=DEBUG
LOG_REQUESTS=true
```

## 📋 Configuration Checklist

### Pre-deployment Checklist
- [ ] Strong `SECRET_KEY` and `ENCRYPTION_KEY` generated
- [ ] Database configured and migrations run
- [ ] Redis connection tested
- [ ] At least one AI provider configured
- [ ] WordPress sites and credentials configured (if using)
- [ ] Security settings appropriate for environment
- [ ] Rate limiting configured
- [ ] Logging configured
- [ ] Health checks working
- [ ] File permissions set correctly
- [ ] Backup strategy in place

### Production Checklist
- [ ] `DEBUG=false`
- [ ] `ENVIRONMENT=production`
- [ ] `FORCE_HTTPS=true`
- [ ] `SESSION_SECURE=true`
- [ ] `ENABLE_SECURITY_HEADERS=true`
- [ ] Strong rate limiting configured
- [ ] Monitoring and alerting set up
- [ ] Regular backups scheduled
- [ ] SSL certificate configured
- [ ] Firewall rules in place
