@echo off
REM Startup script for backend server (Windows)
REM This script activates the virtual environment and starts the FastAPI server

echo Starting Backend Server...
echo.

cd /d "%~dp0"

REM Check if venv exists
if not exist "backend\venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run the setup first:
    echo   cd backend
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    exit /b 1
)

REM Check if requirements are installed
if not exist "backend\venv\Scripts\uvicorn.exe" (
    echo [WARNING] Dependencies may not be installed.
    echo Installing dependencies...
    call backend\venv\Scripts\activate.bat
    pip install -r backend\requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        exit /b 1
    )
)

REM Activate venv and start server
echo Activating virtual environment...
call backend\venv\Scripts\activate.bat

echo.
echo Starting FastAPI server on http://localhost:8000
echo API documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run uvicorn from current directory (project1/) so it can find the backend package
python -m uvicorn backend.main:app --reload --port 8000

