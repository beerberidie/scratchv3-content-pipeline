@echo off
echo Installing Redis for Windows...
echo.

echo 1. Download Redis from GitHub releases
echo 2. Extract to C:\Redis
echo 3. Run redis-server.exe

echo.
echo Manual steps:
echo 1. Go to: https://github.com/microsoftarchive/redis/releases
echo 2. Download Redis-x64-3.0.504.msi
echo 3. Install and start Redis service

echo.
echo Alternative - Using Chocolatey:
echo choco install redis-64

echo.
echo Alternative - Using Docker:
echo docker run -d -p 6379:6379 redis:alpine

pause
