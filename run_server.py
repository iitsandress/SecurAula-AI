#!/usr/bin/env python3
"""
EduMon Server Runner

This script launches the EduMon FastAPI server.
It's the single point of entry for starting the teacher's backend.
"""
import sys
import subprocess
import os

def check_and_install_dependencies():
    """Checks if dependencies are installed and installs them if not."""
    print("Verificando dependencias del servidor...")
    req_path = os.path.join(os.path.dirname(__file__), 'edumon', 'requirements-server.txt')
    
    # Lista de dependencias críticas que deben estar instaladas
    critical_packages = ['jinja2', 'fastapi', 'uvicorn', 'pydantic', 'sqlalchemy', 'aiofiles']
    
    try:
        import importlib.metadata
        
        # Primero verificar dependencias críticas
        missing_critical = []
        for package in critical_packages:
            try:
                importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                missing_critical.append(package)
        
        # Si faltan dependencias críticas, instalarlas primero
        if missing_critical:
            print(f"⚠️  Instalando dependencias críticas: {', '.join(missing_critical)}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_critical)
            print("✅ Dependencias críticas instaladas.")
        
        # Luego verificar el archivo de requirements
        if os.path.exists(req_path):
            with open(req_path, 'r') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            # Check each requirement
            missing_packages = []
            for req in requirements:
                # Parse package name (remove version specifiers)
                package_name = req.split('>=')[0].split('==')[0].split('[')[0].strip()
                try:
                    importlib.metadata.version(package_name)
                except importlib.metadata.PackageNotFoundError:
                    missing_packages.append(req)
            
            if missing_packages:
                print(f"⚠️  Dependencias adicionales faltantes: {', '.join(missing_packages)}. Instalando...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
                print("✅ Todas las dependencias instaladas.")
            else:
                print("✅ Todas las dependencias satisfechas.")
        else:
            print("⚠️  Archivo requirements-server.txt no encontrado. Instalando dependencias básicas...")
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + critical_packages)
            print("✅ Dependencias básicas instaladas.")
            
    except (ImportError, FileNotFoundError):
        print("⚠️  Error verificando dependencias. Instalando dependencias críticas...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + critical_packages)
        if os.path.exists(req_path):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
        print("✅ Dependencias instaladas.")
    except Exception as e:
        print(f"⚠️  Error verificando dependencias: {e}. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + critical_packages)
        if os.path.exists(req_path):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
        print("✅ Dependencias instaladas.")

# --- Main Execution ---
if __name__ == "__main__":
    check_and_install_dependencies()

    # Imports are done after dependency check
    import uvicorn
    from edumon.backend.app.main import app
    from edumon.backend.app.core.config import settings

    print("\n" + "="*60)
    print("🎓 EduMon Server - v4.0.0")
    print("="*60)
    print(f"🔑 Clave de Acceso: {settings.EDUMON_API_KEY}")
    print("✅ Servidor listo y esperando conexiones...")
    print("\n🔗 URLs Disponibles:")
    print(f"   - 📊 Dashboard: http://localhost:8000/dashboard?api_key={settings.EDUMON_API_KEY}")
    print(f"   - 📖 API Docs:  http://localhost:8000/docs")
    print(f"   - ❤️ Health:    http://localhost:8000/health")
    print("\n⚠️  Presiona Ctrl+C para detener el servidor.")
    print("-"*60)

    # Create necessary directories before starting
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.LOG_DIR, exist_ok=True)

    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="warning"
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario.")
    except Exception as e:
        print(f"❌ Error inesperado al lanzar el servidor: {e}")
