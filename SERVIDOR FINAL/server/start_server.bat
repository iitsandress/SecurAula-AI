@echo off
echo ========================================
echo   SecurAula-AI Server Manager
echo ========================================
echo.

REM Check if port 3000 is in use
netstat -ano | findstr :3000 >nul
if %errorlevel% == 0 (
    echo ⚠️  Port 3000 is currently in use!
    echo.
    echo Finding process using port 3000...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
        echo Process ID: %%a
        tasklist /FI "PID eq %%a" /FO TABLE
        echo.
        set /p choice="Do you want to kill this process? (y/n): "
        if /i "!choice!"=="y" (
            taskkill /PID %%a /F
            echo Process terminated.
            goto :start_server
        ) else (
            echo.
            echo You can start the server on a different port:
            echo   set PORT=3001 ^&^& node server.js
            echo.
            pause
            exit /b 1
        )
    )
) else (
    echo ✅ Port 3000 is available
)

:start_server
echo.
echo 🚀 Starting SecurAula-AI server...
echo.
node server.js