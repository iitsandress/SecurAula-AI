#!/bin/bash

# SecurAula-AI / EduMon - Instalador de Dependencias
# Script para Linux/Mac

echo ""
echo "==============================================================="
echo "🔧 INSTALADOR DE DEPENDENCIAS - SecurAula-AI / EduMon"
echo "==============================================================="
echo "📦 Instalando todas las dependencias necesarias..."
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

echo "🐍 Python encontrado"
echo ""

# Hacer el script ejecutable
chmod +x install_dependencies.py

# Ejecutar el instalador
echo "🚀 Ejecutando instalador automático..."
$PYTHON_CMD install_dependencies.py

# Verificar resultado
if [ $? -eq 0 ]; then
    echo ""
    echo "==============================================================="
    echo "🎉 ¡INSTALACIÓN EXITOSA!"
    echo "==============================================================="
    echo "✅ Todas las dependencias están instaladas"
    echo "🚀 Ahora puedes ejecutar: ./iniciar_servidor.sh"
    echo ""
else
    echo ""
    echo "==============================================================="
    echo "⚠️  INSTALACIÓN CON PROBLEMAS"
    echo "==============================================================="
    echo "💡 Intenta instalar manualmente:"
    echo "   pip install -r edumon/backend/requirements.txt"
    echo ""
fi