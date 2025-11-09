#!/usr/bin/env python3
"""
Alternative SSL certificate solutions for public hosting
"""
import os
import requests
import json
from datetime import datetime

def check_domain_status():
    """Check the current status of the domain"""
    domain = "scratchgpt.webhop.me"
    port = "8442"
    
    print(f"🌐 Checking domain status: {domain}:{port}")
    print("=" * 50)
    
    # Test HTTP access
    try:
        response = requests.get(f"http://{domain}:{port}/health", timeout=10)
        print(f"✅ HTTP Access: Working (Status: {response.status_code})")
        http_working = True
    except Exception as e:
        print(f"❌ HTTP Access: Failed ({e})")
        http_working = False
    
    # Test HTTPS access (will fail with self-signed cert)
    try:
        response = requests.get(f"https://{domain}:{port}/health", timeout=10, verify=False)
        print(f"⚠️  HTTPS Access: Working but with self-signed certificate")
        https_working = True
    except Exception as e:
        print(f"❌ HTTPS Access: Failed ({e})")
        https_working = False
    
    return http_working, https_working

def suggest_ssl_solutions():
    """Suggest alternative SSL solutions"""
    print("\n🔐 SSL Certificate Solutions")
    print("=" * 50)
    
    print("\n1. 🆓 ZeroSSL (Free Alternative to Let's Encrypt)")
    print("   - Go to: https://zerossl.com")
    print("   - Create free account")
    print("   - Generate certificate for scratchgpt.webhop.me")
    print("   - Use DNS verification method")
    
    print("\n2. 🔧 SSL For Free")
    print("   - Go to: https://www.sslforfree.com")
    print("   - Enter domain: scratchgpt.webhop.me")
    print("   - Use DNS verification")
    print("   - Download certificate files")
    
    print("\n3. 🛡️ Cloudflare Tunnel (Recommended)")
    print("   - No nameserver changes required!")
    print("   - Go to: https://dash.cloudflare.com")
    print("   - Create account and add domain")
    print("   - Use 'Zero Trust' > 'Tunnels'")
    print("   - Create tunnel pointing to 192.168.1.4:8081")
    
    print("\n4. 🔄 Reverse Proxy with Nginx")
    print("   - Install Nginx on your server")
    print("   - Use Nginx to handle SSL termination")
    print("   - Proxy requests to your application")

def create_nginx_config():
    """Create Nginx configuration for reverse proxy"""
    config = """
# Nginx configuration for Scratch App
server {
    listen 80;
    server_name scratchgpt.webhop.me;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name scratchgpt.webhop.me;
    
    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
    limit_req zone=api burst=20 nodelay;
    
    # Proxy to your application
    location / {
        proxy_pass https://192.168.1.4:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Block common attack paths
    location ~ /(admin|wp-admin|phpmyadmin|config|\.env) {
        deny all;
        return 404;
    }
}
"""
    
    with open("nginx_scratch_app.conf", "w") as f:
        f.write(config)
    
    print("✅ Nginx configuration saved to: nginx_scratch_app.conf")

def create_cloudflare_tunnel_guide():
    """Create guide for Cloudflare Tunnel setup"""
    guide = """
# 🛡️ Cloudflare Tunnel Setup Guide

## Why Cloudflare Tunnel?
- No nameserver changes required
- Free SSL certificates
- DDoS protection
- No port forwarding needed
- Hides your real IP address

## Setup Steps:

### 1. Create Cloudflare Account
- Go to: https://dash.cloudflare.com
- Sign up for free account
- Verify your email

### 2. Add Your Domain
- Click "Add a site"
- Enter: scratchgpt.webhop.me
- Choose "Free" plan
- Skip nameserver changes (we'll use tunnels)

### 3. Create Tunnel
- Go to "Zero Trust" in left sidebar
- Click "Tunnels" under "Access"
- Click "Create a tunnel"
- Name it: "scratch-app-tunnel"
- Choose "Cloudflared" connector

### 4. Install Cloudflared
- Download from: https://github.com/cloudflare/cloudflared/releases
- Windows: Download cloudflared-windows-amd64.exe
- Run the installation command shown in dashboard

### 5. Configure Tunnel
- Public hostname: scratchgpt.webhop.me
- Service type: HTTPS
- URL: https://192.168.1.4:8081

### 6. Start Tunnel
- Run the command provided by Cloudflare
- Your app will be accessible via Cloudflare's network

## Benefits:
✅ Free trusted SSL certificate
✅ DDoS protection
✅ Global CDN
✅ No router configuration needed
✅ Hides your real IP address
✅ Works with No-IP dynamic DNS
"""
    
    with open("CLOUDFLARE_TUNNEL_GUIDE.md", "w") as f:
        f.write(guide)
    
    print("✅ Cloudflare Tunnel guide saved to: CLOUDFLARE_TUNNEL_GUIDE.md")

def main():
    print("🔐 SSL Certificate Alternatives")
    print("Since CloudFlare nameservers aren't working, here are other options:")
    print()
    
    # Check current domain status
    http_ok, https_ok = check_domain_status()
    
    if not http_ok:
        print("\n⚠️  WARNING: Your domain is not accessible via HTTP")
        print("Please check your No-IP configuration and port forwarding")
        return
    
    # Suggest solutions
    suggest_ssl_solutions()
    
    print("\n🎯 RECOMMENDED SOLUTION: Cloudflare Tunnel")
    print("This is the easiest option that doesn't require nameserver changes!")
    
    choice = input("\nWould you like me to create setup guides? (y/n): ").lower()
    
    if choice == 'y':
        create_cloudflare_tunnel_guide()
        create_nginx_config()
        
        print("\n📋 Files created:")
        print("- CLOUDFLARE_TUNNEL_GUIDE.md (Recommended)")
        print("- nginx_scratch_app.conf (Advanced users)")
        
        print("\n🚀 Next Steps:")
        print("1. Follow the Cloudflare Tunnel guide")
        print("2. This will give you free SSL and hide your IP")
        print("3. No router configuration changes needed!")

if __name__ == "__main__":
    main()
