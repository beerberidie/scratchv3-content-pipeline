#!/usr/bin/env python3
"""
Startup script for the Scratch Automation App
"""
import uvicorn
from app.main import app
from app.config import settings

if __name__ == "__main__":
    print("🚀 Starting Scratch Automation App...")
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")
    print(f"Server binding to: {settings.host}:{settings.port}")

    # Determine protocol based on SSL configuration
    protocol = "https" if settings.use_ssl else "http"

    print("📱 Access the application at:")
    print(f"   • {protocol}://localhost:{settings.port}")
    print(f"   • {protocol}://127.0.0.1:{settings.port}")
    if settings.host == "1.1.1.1":
        print(f"   • Or from other devices on your network: {protocol}://192.168.1.4:{settings.port}")
    print()

    # Configure SSL if enabled
    ssl_config = {}
    if settings.use_ssl and settings.ssl_keyfile and settings.ssl_certfile:
        ssl_config = {
            "ssl_keyfile": settings.ssl_keyfile,
            "ssl_certfile": settings.ssl_certfile
        }
        print(f"🔒 SSL enabled with cert: {settings.ssl_certfile}")

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
        **ssl_config
    )
