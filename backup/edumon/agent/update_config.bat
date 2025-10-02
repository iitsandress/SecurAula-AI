@echo off
echo.
echo ========================================
echo  EduMon Agent - Configuration Update
echo ========================================
echo.

cd /d "%~dp0"

python update_config.py

echo.
pause