"""
Enhanced security middleware for public internet hosting
"""
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class PublicSecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced security middleware for public hosting"""
    
    def __init__(self, app):
        super().__init__(app)
        self.blocked_ips = set()
        self.failed_attempts = {}
        
        # Suspicious patterns that indicate attacks
        self.attack_patterns = [
            '/admin', '/wp-admin', '/phpmyadmin', '/.env', '/config',
            '/api/v1', '/swagger-ui', '/docs', '/debug', '/test',
            'SELECT', 'UNION', 'DROP', 'INSERT', 'UPDATE', 'DELETE',
            '<script', 'javascript:', 'eval(', 'exec(',
            '../', '..\\', '/etc/passwd', '/proc/version',
            'cmd=', 'exec=', 'system(', 'shell_exec'
        ]
        
        # Suspicious user agents
        self.suspicious_agents = [
            'sqlmap', 'nikto', 'nmap', 'masscan', 'zap', 'burp',
            'python-requests', 'curl', 'wget', 'scanner', 'bot',
            'crawler', 'spider', 'scraper'
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Get client information
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "").lower()
        path = request.url.path
        
        # Skip security checks for local IPs
        if self._is_private_ip(client_ip):
            return await call_next(request)
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            logger.warning(f"Blocked request from {client_ip}: IP blacklisted")
            return JSONResponse(
                status_code=403,
                content={"error": "Access denied", "code": "IP_BLOCKED"}
            )
        
        # Check for attack patterns in URL
        if self._check_attack_patterns(path):
            logger.warning(f"Attack pattern detected from {client_ip}: {path}")
            self._record_attack(client_ip, f"Attack pattern: {path}")
            return JSONResponse(
                status_code=404,
                content={"error": "Not found"}
            )
        
        # Check for suspicious user agents
        if self._check_suspicious_user_agent(user_agent):
            logger.warning(f"Suspicious user agent from {client_ip}: {user_agent}")
            self._record_attack(client_ip, f"Suspicious UA: {user_agent}")
            return JSONResponse(
                status_code=403,
                content={"error": "Access denied", "code": "SUSPICIOUS_CLIENT"}
            )
        
        # Check request size (prevent large payload attacks)
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            logger.warning(f"Large request from {client_ip}: {content_length} bytes")
            return JSONResponse(
                status_code=413,
                content={"error": "Request too large"}
            )
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Add security headers for public access
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
            response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing request from {client_ip}: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get the real client IP, considering proxies"""
        # Check for forwarded headers (in case of reverse proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is from private network"""
        try:
            import ipaddress
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except:
            return False
    
    def _check_attack_patterns(self, path: str) -> bool:
        """Check if path contains attack patterns"""
        path_lower = path.lower()
        for pattern in self.attack_patterns:
            if pattern.lower() in path_lower:
                return True
        return False
    
    def _check_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is suspicious"""
        if not user_agent or len(user_agent) < 10:
            return True
        
        for agent in self.suspicious_agents:
            if agent in user_agent:
                return True
        return False
    
    def _record_attack(self, ip: str, reason: str):
        """Record an attack attempt and potentially block the IP"""
        from datetime import datetime, timedelta
        
        current_time = datetime.utcnow()
        
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = []
        
        # Clean old attempts (older than 1 hour)
        self.failed_attempts[ip] = [
            attempt for attempt in self.failed_attempts[ip]
            if current_time - attempt['time'] < timedelta(hours=1)
        ]
        
        # Add new attempt
        self.failed_attempts[ip].append({
            'time': current_time,
            'reason': reason
        })
        
        # Block IP if too many attempts
        if len(self.failed_attempts[ip]) >= 3:
            self.blocked_ips.add(ip)
            logger.error(f"BLOCKED IP {ip} after {len(self.failed_attempts[ip])} attacks: {reason}")
    
    def get_security_stats(self) -> dict:
        """Get current security statistics"""
        return {
            'blocked_ips': len(self.blocked_ips),
            'failed_attempts': sum(len(attempts) for attempts in self.failed_attempts.values()),
            'unique_attackers': len(self.failed_attempts)
        }
