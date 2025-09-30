@echo off
chcp 65001 >nul
title SecurAula-AI / EduMon - Servidor Automatizado

echo.
echo ===============================================================
echo 🎓 SECURAAULA-AI / EDUMON - SERVIDOR AUTOMATIZADO
echo ===============================================================
echo 🚀 Iniciando servidor completo con Docker...
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH
    echo 📥 Por favor instala Python desde: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Ejecutar el script de Python
echo 🐍 Ejecutando script de automatización...
python run_server.py

REM Si el script termina, mostrar mensaje
echo.
echo ===============================================================
echo 🏁 Script terminado
echo ===============================================================
echo.
pause