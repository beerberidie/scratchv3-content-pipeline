# 🛡️ Cloudflare Tunnel Setup Guide

## Why Cloudflare Tunnel?
- ✅ **No nameserver changes required**
- ✅ **Free SSL certificates**
- ✅ **DDoS protection**
- ✅ **No port forwarding needed**
- ✅ **Hides your real IP address**
- ✅ **Works with No-IP dynamic DNS**

## Setup Steps:

### 1. Create Cloudflare Account
- Go to: https://dash.cloudflare.com
- Sign up for free account
- Verify your email

### 2. Add Your Domain
- Click "Add a site"
- Enter: `scratchgpt.webhop.me`
- Choose "Free" plan
- **SKIP nameserver changes** (we'll use tunnels instead)

### 3. Access Zero Trust Dashboard
- In Cloudflare dashboard, click "Zero Trust" in left sidebar
- If prompted, set up Zero Trust (it's free)
- Go to "Networks" > "Tunnels"

### 4. Create Tunnel
- Click "Create a tunnel"
- Choose "Cloudflared"
- Name it: `scratch-app-tunnel`
- Click "Save tunnel"

### 5. Install Cloudflared
**For Windows:**
- Download from: https://github.com/cloudflare/cloudflared/releases
- Download: `cloudflared-windows-amd64.exe`
- Rename to: `cloudflared.exe`
- Place in a folder like: `C:\cloudflared\`
- Add to PATH or run from that folder

**Installation Command (shown in dashboard):**
```bash
cloudflared.exe service install [YOUR-TOKEN-HERE]
```

### 6. Configure Public Hostname
- In the tunnel configuration:
  - **Public hostname**: `scratchgpt.webhop.me`
  - **Service type**: `HTTPS`
  - **URL**: `https://192.168.1.4:8081`
- Click "Save hostname"

### 7. Start the Tunnel
Run the command provided by Cloudflare:
```bash
cloudflared.exe tunnel run scratch-app-tunnel
```

### 8. Test Access
- Your app will be accessible at: `https://scratchgpt.webhop.me`
- It will have a trusted SSL certificate
- All traffic goes through Cloudflare's network

## Benefits:
✅ **Free trusted SSL certificate**
✅ **DDoS protection**
✅ **Global CDN**
✅ **No router configuration needed**
✅ **Hides your real IP address**
✅ **Works with existing No-IP setup**
✅ **No nameserver changes required**

## Security Advantages:
- Your real IP address is hidden
- Cloudflare filters malicious traffic
- Automatic SSL/TLS encryption
- Protection against common attacks
- Rate limiting at edge locations

## Troubleshooting:
- If tunnel doesn't start, check the token
- Make sure your local app is running on 192.168.1.4:8081
- Check Windows Firewall isn't blocking cloudflared
- Restart the tunnel service if needed

This is the **RECOMMENDED** solution for your setup!
