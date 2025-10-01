@echo off
echo.
echo ========================================
echo   EduMon Server - Programa del Profesor
echo ========================================
echo.

cd /d "%~dp0"

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado
    echo Por favor instala Python 3.11 o superior
    pause
    exit /b 1
)

echo Python encontrado!
echo.

echo Configurando variables de entorno...
set EDUMON_API_KEY=S1R4X
echo API Key configurada: %EDUMON_API_KEY%
echo.

echo Cambiando al directorio del servidor...
cd server

echo Instalando/verificando dependencias...
python -m pip install -r requirements.txt

echo.
echo ========================================
echo   SERVIDOR INICIADO
echo ========================================
echo.
echo Dashboard: http://190.84.119.196:8000/dashboard
echo API Docs:  http://190.84.119.196:8000/docs
echo Health:    http://190.84.119.196:8000/health
echo.
echo Presiona Ctrl+C para detener
echo ========================================
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo Servidor detenido.
pause