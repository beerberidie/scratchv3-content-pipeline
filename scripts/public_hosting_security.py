#!/usr/bin/env python3
"""
Additional security measures for public hosting
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Set
import ipaddress

logger = logging.getLogger(__name__)

class PublicHostingSecurity:
    """Enhanced security measures for public internet hosting"""
    
    def __init__(self):
        self.failed_attempts: Dict[str, list] = {}
        self.blocked_ips: Set[str] = set()
        self.suspicious_patterns = [
            '/admin', '/wp-admin', '/phpmyadmin', '/.env', '/config',
            '/api/v1', '/swagger', '/docs', '/debug', '/test',
            'SELECT', 'UNION', 'DROP', 'INSERT', 'UPDATE', 'DELETE',
            '<script', 'javascript:', 'eval(', 'exec(',
            '../', '..\\', '/etc/passwd', '/proc/version'
        ]
        self.load_blocked_ips()
    
    def load_blocked_ips(self):
        """Load previously blocked IPs from file"""
        try:
            if os.path.exists('data/blocked_ips.json'):
                with open('data/blocked_ips.json', 'r') as f:
                    data = json.load(f)
                    self.blocked_ips = set(data.get('blocked_ips', []))
                    logger.info(f"Loaded {len(self.blocked_ips)} blocked IPs")
        except Exception as e:
            logger.error(f"Error loading blocked IPs: {e}")
    
    def save_blocked_ips(self):
        """Save blocked IPs to file"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/blocked_ips.json', 'w') as f:
                json.dump({
                    'blocked_ips': list(self.blocked_ips),
                    'updated_at': datetime.utcnow().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving blocked IPs: {e}")
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        return ip in self.blocked_ips
    
    def block_ip(self, ip: str, reason: str = "Security violation"):
        """Block an IP address"""
        self.blocked_ips.add(ip)
        self.save_blocked_ips()
        logger.warning(f"Blocked IP {ip}: {reason}")
    
    def record_failed_attempt(self, ip: str, endpoint: str = ""):
        """Record a failed login or suspicious attempt"""
        current_time = datetime.utcnow()
        
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = []
        
        # Clean old attempts (older than 1 hour)
        self.failed_attempts[ip] = [
            attempt for attempt in self.failed_attempts[ip]
            if current_time - datetime.fromisoformat(attempt['time']) < timedelta(hours=1)
        ]
        
        # Add new attempt
        self.failed_attempts[ip].append({
            'time': current_time.isoformat(),
            'endpoint': endpoint
        })
        
        # Block IP if too many failed attempts
        if len(self.failed_attempts[ip]) >= 5:
            self.block_ip(ip, f"Too many failed attempts ({len(self.failed_attempts[ip])})")
    
    def check_suspicious_request(self, path: str, user_agent: str = "", ip: str = "") -> bool:
        """Check if request contains suspicious patterns"""
        
        # Check for suspicious patterns in path
        path_lower = path.lower()
        for pattern in self.suspicious_patterns:
            if pattern.lower() in path_lower:
                logger.warning(f"Suspicious request from {ip}: {path}")
                if ip:
                    self.record_failed_attempt(ip, path)
                return True
        
        # Check for suspicious user agents
        suspicious_agents = [
            'sqlmap', 'nikto', 'nmap', 'masscan', 'zap', 'burp',
            'python-requests', 'curl', 'wget', 'scanner'
        ]
        
        if user_agent:
            user_agent_lower = user_agent.lower()
            for agent in suspicious_agents:
                if agent in user_agent_lower:
                    logger.warning(f"Suspicious user agent from {ip}: {user_agent}")
                    if ip:
                        self.record_failed_attempt(ip, f"Suspicious UA: {user_agent}")
                    return True
        
        return False
    
    def is_private_ip(self, ip: str) -> bool:
        """Check if IP is from private network"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except:
            return False
    
    def get_security_report(self) -> dict:
        """Generate security report"""
        return {
            'blocked_ips_count': len(self.blocked_ips),
            'blocked_ips': list(self.blocked_ips),
            'failed_attempts_count': sum(len(attempts) for attempts in self.failed_attempts.values()),
            'unique_attackers': len(self.failed_attempts),
            'report_time': datetime.utcnow().isoformat()
        }

# Global security instance
public_security = PublicHostingSecurity()

def check_request_security(request_path: str, client_ip: str, user_agent: str = "") -> bool:
    """
    Check if request should be blocked
    Returns True if request should be blocked
    """
    
    # Always allow private IPs (local network)
    if public_security.is_private_ip(client_ip):
        return False
    
    # Check if IP is blocked
    if public_security.is_ip_blocked(client_ip):
        logger.warning(f"Blocked request from {client_ip}: IP is blacklisted")
        return True
    
    # Check for suspicious patterns
    if public_security.check_suspicious_request(request_path, user_agent, client_ip):
        return True
    
    return False

if __name__ == "__main__":
    # Test the security system
    print("🛡️  Public Hosting Security System")
    print("Testing security checks...")
    
    # Test suspicious requests
    test_cases = [
        ("/api/tasks/", "192.168.1.100", "Mozilla/5.0"),  # Should pass (private IP)
        ("/admin/login", "203.0.113.1", "Mozilla/5.0"),   # Should block (suspicious path)
        ("/api/tasks/", "203.0.113.2", "sqlmap/1.0"),     # Should block (suspicious UA)
        ("/", "203.0.113.3", "Mozilla/5.0"),              # Should pass (normal request)
    ]
    
    for path, ip, ua in test_cases:
        blocked = check_request_security(path, ip, ua)
        status = "BLOCKED" if blocked else "ALLOWED"
        print(f"{status}: {ip} -> {path} (UA: {ua[:20]}...)")
    
    # Show security report
    report = public_security.get_security_report()
    print(f"\nSecurity Report:")
    print(f"- Blocked IPs: {report['blocked_ips_count']}")
    print(f"- Failed attempts: {report['failed_attempts_count']}")
    print(f"- Unique attackers: {report['unique_attackers']}")
