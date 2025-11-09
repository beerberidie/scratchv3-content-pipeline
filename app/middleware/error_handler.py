"""
Global error handling middleware
"""
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            # Log HTTP exceptions (but don't log rate limit exceptions as warnings)
            if exc.status_code == 429:
                logger.info(f"Rate limit exceeded: {exc.detail} - {request.url}")
            else:
                logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")

            # Re-raise HTTPException to let FastAPI handle it properly
            raise exc
        except Exception as exc:
            # Log unexpected errors
            logger.error(f"Unexpected error: {str(exc)} - {request.url}", exc_info=True)
            
            # Return generic error in production, detailed in development
            if settings.debug:
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": str(exc),
                        "type": type(exc).__name__,
                        "status_code": 500
                    }
                )
            else:
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal server error",
                        "status_code": 500
                    }
                )
