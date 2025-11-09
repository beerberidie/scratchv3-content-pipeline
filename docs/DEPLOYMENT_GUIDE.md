# 🚀 ScratchV3 Deployment Guide

Complete guide for deploying ScratchV3 to production environments with scaling considerations.

## 📋 Pre-Deployment Checklist

### ✅ Environment Preparation
- [ ] Production server with Python 3.8+ installed
- [ ] Redis server configured and running
- [ ] Database server (PostgreSQL recommended for production)
- [ ] SSL certificate for HTTPS
- [ ] Domain name configured
- [ ] Firewall rules configured
- [ ] Backup strategy in place

### ✅ Application Configuration
- [ ] `.env` file configured with production values
- [ ] `DEBUG=false` and `ENVIRONMENT=production`
- [ ] Strong `SECRET_KEY` and `ENCRYPTION_KEY` generated
- [ ] API keys configured and tested
- [ ] WordPress sites and credentials configured
- [ ] Database migrations run successfully
- [ ] Static files properly served

### ✅ Security Configuration
- [ ] HTTPS enabled (`FORCE_HTTPS=true`)
- [ ] Secure session settings (`SESSION_SECURE=true`)
- [ ] Security headers enabled (`ENABLE_SECURITY_HEADERS=true`)
- [ ] Rate limiting configured appropriately
- [ ] File upload restrictions in place
- [ ] API key encryption verified

## 🐳 Docker Deployment (Recommended)

### 1. Create Dockerfile
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/tasks data/history data/chats data/user_keys data/wp_sites data/wp_auth uploads

# Set permissions
RUN chmod -R 755 data uploads

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "run.py"]
```

### 2. Create docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/scratchv3
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=production
      - DEBUG=false
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
    depends_on:
      - db
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: scratchv3
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 3. Deploy with Docker
```bash
# Clone repository
git clone <repository-url>
cd ScratchV3

# Configure environment
cp .env.example .env
# Edit .env with production values

# Set database password
export POSTGRES_PASSWORD=your-secure-password

# Build and start services
docker-compose up -d

# Run database migrations
docker-compose exec app alembic upgrade head

# Check service health
docker-compose ps
docker-compose logs app
```

## 🖥️ Traditional Server Deployment

### 1. Server Setup (Ubuntu/Debian)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip nginx postgresql redis-server

# Create application user
sudo useradd -m -s /bin/bash scratchv3
sudo usermod -aG www-data scratchv3
```

### 2. Application Setup
```bash
# Switch to application user
sudo su - scratchv3

# Clone repository
git clone <repository-url>
cd ScratchV3

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production values

# Create data directories
mkdir -p data/{tasks,history,chats,user_keys,wp_sites,wp_auth} uploads
chmod -R 755 data uploads
```

### 3. Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres createdb scratchv3
sudo -u postgres createuser scratchv3
sudo -u postgres psql -c "ALTER USER scratchv3 WITH PASSWORD 'your-password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE scratchv3 TO scratchv3;"

# Run migrations
cd /home/scratchv3/ScratchV3
source venv/bin/activate
alembic upgrade head
```

### 4. Process Management with Systemd
```bash
# Create systemd service file
sudo tee /etc/systemd/system/scratchv3.service > /dev/null <<EOF
[Unit]
Description=ScratchV3 Application
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=scratchv3
Group=scratchv3
WorkingDirectory=/home/scratchv3/ScratchV3
Environment=PATH=/home/scratchv3/ScratchV3/venv/bin
ExecStart=/home/scratchv3/ScratchV3/venv/bin/python run.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable scratchv3
sudo systemctl start scratchv3
sudo systemctl status scratchv3
```

### 5. Nginx Configuration
```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/scratchv3 > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static/ {
        alias /home/scratchv3/ScratchV3/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/scratchv3 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## ☁️ Cloud Platform Deployment

### AWS Deployment
```bash
# Using AWS ECS with Fargate
aws ecs create-cluster --cluster-name scratchv3-cluster

# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
    --cluster scratchv3-cluster \
    --service-name scratchv3-service \
    --task-definition scratchv3:1 \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

### Google Cloud Platform
```bash
# Deploy to Cloud Run
gcloud run deploy scratchv3 \
    --image gcr.io/your-project/scratchv3 \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars ENVIRONMENT=production
```

### Azure Container Instances
```bash
# Deploy to Azure
az container create \
    --resource-group scratchv3-rg \
    --name scratchv3-app \
    --image your-registry/scratchv3:latest \
    --dns-name-label scratchv3 \
    --ports 8000 \
    --environment-variables ENVIRONMENT=production
```

## 📊 Monitoring & Maintenance

### 1. Health Monitoring
```bash
# Check application health
curl -f https://your-domain.com/health

# Monitor logs
sudo journalctl -u scratchv3 -f

# Check resource usage
htop
df -h
free -h
```

### 2. Backup Strategy
```bash
# Database backup script
#!/bin/bash
BACKUP_DIR="/home/scratchv3/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h localhost -U scratchv3 scratchv3 > $BACKUP_DIR/db_backup_$DATE.sql

# Backup data files
tar -czf $BACKUP_DIR/data_backup_$DATE.tar.gz /home/scratchv3/ScratchV3/data

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### 3. Log Rotation
```bash
# Configure logrotate
sudo tee /etc/logrotate.d/scratchv3 > /dev/null <<EOF
/home/scratchv3/ScratchV3/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 scratchv3 scratchv3
    postrotate
        systemctl reload scratchv3
    endscript
}
EOF
```

## 🔧 Scaling Considerations

### Horizontal Scaling
- Use load balancer (nginx, HAProxy, or cloud LB)
- Deploy multiple application instances
- Shared Redis and database
- Sticky sessions for user authentication

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Optimize database queries
- Implement caching strategies
- Monitor resource usage

### Performance Optimization
- Enable Redis caching
- Optimize database indexes
- Use CDN for static files
- Implement request compression
- Monitor and tune rate limits

## 🚨 Troubleshooting

### Common Issues
1. **Application won't start**: Check logs, environment variables, dependencies
2. **Database connection failed**: Verify credentials, network connectivity
3. **Redis connection failed**: Check Redis service status, configuration
4. **High memory usage**: Monitor task queue, implement cleanup
5. **Slow response times**: Check database performance, Redis connectivity

### Debug Commands
```bash
# Check service status
sudo systemctl status scratchv3 postgresql redis

# View logs
sudo journalctl -u scratchv3 -n 100
tail -f /var/log/nginx/error.log

# Test connectivity
redis-cli ping
psql -h localhost -U scratchv3 -d scratchv3 -c "SELECT 1;"

# Monitor resources
htop
iotop
netstat -tulpn
```

## 📋 Post-Deployment Checklist

- [ ] Application starts successfully
- [ ] Health check endpoint responds
- [ ] Database connectivity verified
- [ ] Redis connectivity verified
- [ ] HTTPS working correctly
- [ ] API key validation working
- [ ] WordPress integration tested
- [ ] Task scheduling functional
- [ ] File uploads working
- [ ] Backup system configured
- [ ] Monitoring alerts set up
- [ ] Log rotation configured
- [ ] Security scan completed
- [ ] Performance baseline established
