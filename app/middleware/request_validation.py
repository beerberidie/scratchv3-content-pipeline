"""
Request validation middleware to handle malformed requests gracefully
"""
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.exceptions import HTTPException

logger = logging.getLogger(__name__)


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle malformed HTTP requests gracefully"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            # Basic request validation
            if not hasattr(request, 'method') or not request.method:
                logger.debug("Invalid request: missing method")
                return Response(
                    content="Bad Request: Invalid HTTP method",
                    status_code=400,
                    media_type="text/plain"
                )
            
            # Check for valid HTTP methods
            valid_methods = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'}
            if request.method not in valid_methods:
                logger.debug(f"Invalid request: unsupported method {request.method}")
                return Response(
                    content="Bad Request: Unsupported HTTP method",
                    status_code=405,
                    media_type="text/plain"
                )
            
            # Proceed with the request
            response = await call_next(request)
            return response
            
        except UnicodeDecodeError:
            logger.debug("Invalid request: Unicode decode error")
            return Response(
                content="Bad Request: Invalid encoding",
                status_code=400,
                media_type="text/plain"
            )
        except Exception as exc:
            # Log but don't spam the logs with common invalid request patterns
            if "Invalid HTTP request" not in str(exc):
                logger.debug(f"Request validation error: {str(exc)}")
            
            return Response(
                content="Bad Request: Malformed request",
                status_code=400,
                media_type="text/plain"
            )
