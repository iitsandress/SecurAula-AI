#!/usr/bin/env python3
"""
Script para ejecutar el servidor EduMon
"""
import os
import sys
import subprocess

def main():
    print("🎓 Iniciando EduMon Server (Programa del Profesor)")
    print("=" * 50)
    
    # Cambiar al directorio del servidor
    server_dir = os.path.join(os.path.dirname(__file__), "server")
    os.chdir(server_dir)
    
    print(f"📁 Directorio de trabajo: {os.getcwd()}")
    
    # Configurar variables de entorno
    os.environ["EDUMON_API_KEY"] = "S1R4X"
    print(f"🔑 API Key configurada: {os.environ.get('EDUMON_API_KEY')}")
    
    # Verificar si las dependencias están instaladas
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ Dependencias encontradas")
    except ImportError as e:
        print(f"❌ Falta dependencia: {e}")
        print("💡 Instalando dependencias...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencias instaladas")
        except subprocess.CalledProcessError:
            print("❌ Error instalando dependencias")
            return 1
    
    # Ejecutar el servidor
    print("\n🚀 Iniciando servidor...")
    print("📊 Dashboard disponible en: http://0.0.0.0:8000/dashboard")
    print("🔧 API disponible en: http://0.0.0.0:8000/docs")
    print("❤️  Health check: http://0.0.0.0:8000/health")
    print("\n⚠️  Presiona Ctrl+C para detener el servidor")
    print("=" * 50)
    
    try:
        # Importar y ejecutar la aplicación
        sys.path.insert(0, os.getcwd())
        
        # Ejecutar con uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
        return 0
    except Exception as e:
        print(f"\n❌ Error ejecutando servidor: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())