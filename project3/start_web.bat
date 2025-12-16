@echo off
echo Starting project3 web server...
echo.
cd /d %~dp0
call venv\Scripts\activate
python -m src.main serve
pause

