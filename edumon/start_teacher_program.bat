@echo off
title EduMon - Programa del Profesor
color 0A

echo.
echo  ███████╗██████╗ ██╗   ██╗███╗   ███╗ ██████╗ ███╗   ██╗
echo  ██╔════╝██╔══██╗██║   ██║████╗ ████║██╔═══██╗████╗  ██║
echo  █████╗  ██║  ██║██║   ██║██╔████╔██║██║   ██║██╔██╗ ██║
echo  ██╔══╝  ██║  ██║██║   ██║██║╚██╔╝██║██║   ██║██║╚██╗██║
echo  ███████╗██████╔╝╚██████╔╝██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
echo  ╚══════╝╚═════╝  ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
echo.
echo                    PROGRAMA DEL PROFESOR
echo  ================================================================
echo.

cd /d "%~dp0"

echo [INFO] Activando entorno virtual...
call .venv\Scripts\activate.bat

echo [INFO] Configurando variables de entorno...
set EDUMON_API_KEY=S1R4X
set PYTHONPATH=%CD%

echo [INFO] Cambiando al directorio del servidor...
cd edumon\server

echo [INFO] Verificando dependencias...
python -c "import fastapi, uvicorn, pydantic; print('[OK] Dependencias encontradas')" 2>nul
if errorlevel 1 (
    echo [WARN] Instalando dependencias faltantes...
    pip install fastapi uvicorn pydantic
)

echo.
echo  ================================================================
echo                        SERVIDOR INICIADO
echo  ================================================================
echo.
echo   📊 Dashboard del Profesor: http://localhost:8000/dashboard
echo   🔧 Documentación API:      http://localhost:8000/docs  
echo   ❤️  Estado del servidor:   http://localhost:8000/health
echo   🔑 API Key configurada:    %EDUMON_API_KEY%
echo.
echo   💡 INSTRUCCIONES:
echo   1. Abre el dashboard en tu navegador
echo   2. Los estudiantes deben ejecutar el agente
echo   3. Monitorea las métricas en tiempo real
echo.
echo   ⚠️  Presiona Ctrl+C para detener el servidor
echo  ================================================================
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo [INFO] Servidor detenido.
echo [INFO] Presiona cualquier tecla para salir...
pause >nul