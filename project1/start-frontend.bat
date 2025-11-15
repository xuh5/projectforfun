@echo off
REM Startup script for frontend server (Windows)
REM This script checks dependencies and starts the Next.js dev server

echo Starting Frontend Server...
echo.

cd /d "%~dp0"

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo [WARNING] Dependencies not installed. Installing...
    cd frontend
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        exit /b 1
    )
    cd ..
)

REM Check if package.json exists
if not exist "frontend\package.json" (
    echo [ERROR] Frontend directory not found or invalid!
    exit /b 1
)

echo Starting Next.js development server...
echo.
echo Frontend will be available at http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

cd frontend
call npm run dev

