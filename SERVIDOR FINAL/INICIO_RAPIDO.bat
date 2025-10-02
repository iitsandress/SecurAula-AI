@echo off
echo ========================================
echo   SecurAula-AI - Inicio Rapido
echo ========================================
echo.

echo [1/3] Iniciando servidor Node.js...
cd server
start "SecurAula Server" cmd /k "echo Servidor SecurAula-AI && node server.js"
cd ..

echo [2/3] Esperando 3 segundos para que el servidor inicie...
timeout /t 3 /nobreak >nul

echo [3/3] Iniciando ngrok tunnel...
start "Ngrok Tunnel" cmd /k "echo Ngrok Tunnel && ngrok http 3000"

echo.
echo ========================================
echo   SISTEMA INICIADO
echo ========================================
echo.
echo 1. Servidor Node.js: http://localhost:3000
echo 2. Ngrok tunnel: Revisa la ventana de ngrok para la URL publica
echo 3. Para ejecutar el agente:
echo    cd agent
echo    python main_simple_windows.py
echo.
echo Presiona cualquier tecla para continuar...
pause >nul