"""
Rate limiting middleware for API endpoints
"""
import time
import logging
from typing import Dict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent API abuse"""
    
    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, list] = {}
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for static files and health checks
        if request.url.path.startswith("/static") or request.url.path == "/health":
            return await call_next(request)

        try:
            # Get client IP - handle case where it might be None
            client_ip = request.client.host if request.client and request.client.host else "unknown"
            current_time = time.time()

            # Initialize client tracking if not exists
            if client_ip not in self.requests:
                self.requests[client_ip] = []

            # Clean old requests (older than 1 hour)
            old_count = len(self.requests[client_ip])
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < 3600  # 1 hour
            ]
            new_count = len(self.requests[client_ip])

            # Log rate limiting info for debugging
            logger.debug(f"Rate limit check for {client_ip}: {new_count}/{settings.max_requests_per_hour} requests (cleaned {old_count - new_count} old requests)")

            # Check rate limit
            if len(self.requests[client_ip]) >= settings.max_requests_per_hour:
                logger.warning(f"Rate limit exceeded for IP {client_ip}. Requests: {len(self.requests[client_ip])}/{settings.max_requests_per_hour}")
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Maximum {settings.max_requests_per_hour} requests per hour reached."
                )

            # Add current request
            self.requests[client_ip].append(current_time)

            # Process request
            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(settings.max_requests_per_hour)
            response.headers["X-RateLimit-Remaining"] = str(
                settings.max_requests_per_hour - len(self.requests[client_ip])
            )
            response.headers["X-RateLimit-Reset"] = str(int(current_time + 3600))

            return response

        except HTTPException:
            # Re-raise HTTPExceptions (like rate limit exceeded)
            raise
        except Exception as e:
            # Log other exceptions and let them propagate
            logger.error(f"Error in rate limiting middleware: {e}")
            # Continue processing the request if rate limiting fails
            return await call_next(request)
