"""
Main FastAPI application for Scratch Automation App
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.config import settings
from app.api import auth, tasks, content, settings as settings_api, history, images, email, scheduler, wordpress, keys, wp, security
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.public_security import PublicSecurityMiddleware
from app.middleware.request_validation import RequestValidationMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage application lifespan"""
    # Startup
    from app.services.scheduler import start_scheduler
    await start_scheduler()
    yield
    # Shutdown
    from app.services.scheduler import stop_scheduler
    await stop_scheduler()


# Create FastAPI app
app = FastAPI(
    title="Scratch Automation App",
    description="AI-powered content generation and automation platform",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware
allowed_origins = ["*"] if settings.debug else [
    "https://scratchgpt.webhop.me:8442",
    "http://scratchgpt.webhop.me:8442",
    "https://192.168.1.4:8081",
    "http://192.168.1.4:8081",
    "https://localhost:8081",
    "http://localhost:8081",
    "https://127.0.0.1:8081",
    "http://127.0.0.1:8081"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware (order matters - ErrorHandler should be outermost)
app.add_middleware(PublicSecurityMiddleware)  # First line of defense
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestValidationMiddleware)  # Validate requests before processing
app.add_middleware(ErrorHandlerMiddleware)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(content.router, prefix="/api/content", tags=["Content Generation"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["Settings"])
app.include_router(history.router, prefix="/api/history", tags=["History"])
app.include_router(images.router, prefix="/api/images", tags=["Images"])
app.include_router(email.router, prefix="/api/email", tags=["Email"])
app.include_router(wordpress.router, prefix="/api/wordpress", tags=["WordPress"])
app.include_router(scheduler.router, prefix="/api/scheduler", tags=["Scheduler"])
app.include_router(keys.router, prefix="/api/keys", tags=["API Keys"])
app.include_router(wp.router, prefix="/api/wp", tags=["WordPress Settings"])
app.include_router(security.router, prefix="/api/security", tags=["Security"])

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the login page"""
    try:
        with open("login.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Login page not found")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard page"""
    try:
        with open("Dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dashboard page not found")

@app.get("/favicon.ico")
async def favicon_ico():
    """Serve the favicon as ICO (redirect to SVG)"""
    return FileResponse("static/favicon.svg", media_type="image/svg+xml")

@app.get("/favicon.svg")
async def favicon_svg():
    """Serve the favicon as SVG"""
    return FileResponse("static/favicon.svg", media_type="image/svg+xml")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.services.scheduler import task_scheduler

    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0",
        "scheduler_running": task_scheduler.is_running,
        "scheduled_jobs": len(task_scheduler.get_scheduled_jobs()) if task_scheduler.is_running else 0
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )
