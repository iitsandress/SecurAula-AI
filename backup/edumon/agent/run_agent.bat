@echo off
echo.
echo ========================================
echo  EduMon Agent - Quick Start
echo ========================================
echo.

cd /d "%~dp0"

echo Checking configuration...
if not exist config.json (
    echo ERROR: config.json not found!
    echo Please run update_config.bat first to configure the agent.
    echo.
    pause
    exit /b 1
)

echo Starting EduMon Agent (Simple Version)...
echo.
echo Press Ctrl+C to stop the agent
echo.

python main_simple.py

echo.
echo Agent stopped.
pause