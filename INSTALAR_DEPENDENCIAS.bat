@echo off
chcp 65001 >nul
title SecurAula-AI - Instalador de Dependencias

echo.
echo ===============================================================
echo 🔧 INSTALADOR DE DEPENDENCIAS - SecurAula-AI / EduMon
echo ===============================================================
echo 📦 Instalando todas las dependencias necesarias...
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

echo 🐍 Python encontrado
echo.

REM Ejecutar el instalador
echo Ejecutando instalador automatico...
python install_simple.py

REM Verificar resultado
if errorlevel 1 (
    echo.
    echo ===============================================================
    echo ⚠️  INSTALACIÓN CON PROBLEMAS
    echo ===============================================================
    echo 💡 Intenta instalar manualmente:
    echo    pip install -r edumon/backend/requirements.txt
    echo.
) else (
    echo.
    echo ===============================================================
    echo 🎉 ¡INSTALACIÓN EXITOSA!
    echo ===============================================================
    echo ✅ Todas las dependencias están instaladas
    echo 🚀 Ahora puedes ejecutar: INICIAR_SERVIDOR.bat
    echo.
)

pause