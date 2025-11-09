"""
Security headers middleware for enhanced protection
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Only add security headers in production or when explicitly enabled
        if not settings.debug or getattr(settings, 'enable_security_headers', False):
            # Prevent MIME type sniffing
            response.headers["X-Content-Type-Options"] = "nosniff"
            
            # Prevent clickjacking
            response.headers["X-Frame-Options"] = "DENY"
            
            # XSS Protection (legacy but still useful)
            response.headers["X-XSS-Protection"] = "1; mode=block"
            
            # Referrer Policy
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
            # Content Security Policy (basic)
            csp_policy = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
            response.headers["Content-Security-Policy"] = csp_policy
            
            # HTTPS Strict Transport Security (only if using HTTPS)
            if request.url.scheme == "https" or getattr(settings, 'use_ssl', False):
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
            # Permissions Policy (restrict dangerous features)
            response.headers["Permissions-Policy"] = (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=()"
            )
        
        return response
