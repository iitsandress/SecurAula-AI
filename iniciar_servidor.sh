#!/bin/bash

# SecurAula-AI / EduMon - Servidor Automatizado
# Script para Linux/Mac

echo ""
echo "==============================================================="
echo "🎓 SECURAAULA-AI / EDUMON - SERVIDOR AUTOMATIZADO"
echo "==============================================================="
echo "🚀 Iniciando servidor completo con Docker..."
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python no está instalado"
        echo "📥 Por favor instala Python desde: https://www.python.org/downloads/"
        echo ""
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Hacer el script ejecutable
chmod +x run_server.py

# Ejecutar el script de Python
echo "🐍 Ejecutando script de automatización..."
$PYTHON_CMD run_server.py

# Si el script termina, mostrar mensaje
echo ""
echo "==============================================================="
echo "🏁 Script terminado"
echo "==============================================================="
echo ""