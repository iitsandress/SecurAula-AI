#!/usr/bin/env python3
"""
Instalador simple y compatible con Windows para SecurAula-AI / EduMon
"""
import sys
import subprocess
import os
from pathlib import Path

# Fix encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def print_header():
    print("\n" + "="*60)
    print("INSTALADOR DE DEPENDENCIAS - SecurAula-AI")
    print("="*60)

def check_python_version():
    """Verificar versión de Python"""
    print("[INFO] Verificando Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"[ERROR] Python {version.major}.{version.minor} no es compatible")
        print("[INFO] Se requiere Python 3.7 o superior")
        return False
    
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro} OK")
    return True

def install_package(package):
    """Instalar un paquete específico"""
    try:
        print(f"[INFO] Instalando {package}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"[OK] {package} instalado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error instalando {package}: {e}")
        return False

def install_from_requirements():
    """Instalar desde archivo requirements"""
    req_file = Path("edumon/backend/requirements.txt")
    
    if not req_file.exists():
        print("[ERROR] Archivo requirements.txt no encontrado")
        return False
    
    print("[INFO] Instalando desde requirements.txt...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
            capture_output=True,
            text=True,
            check=True
        )
        print("[OK] Dependencias del backend instaladas")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error instalando requirements: {e}")
        print("[INFO] Intentando instalacion individual...")
        return False

def install_critical_packages():
    """Instalar paquetes críticos uno por uno"""
    print("[INFO] Instalando paquetes criticos...")
    
    critical_packages = [
        "fastapi>=0.110.0",
        "uvicorn[standard]>=0.23.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.0.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "aiofiles>=23.2.1",
        "requests>=2.31.0",
        "python-multipart>=0.0.6",
        "jinja2>=3.1.0"
    ]
    
    success_count = 0
    for package in critical_packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n[INFO] Resultado: {success_count}/{len(critical_packages)} paquetes instalados")
    return success_count == len(critical_packages)

def upgrade_pip():
    """Actualizar pip"""
    print("[INFO] Actualizando pip...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
            text=True,
            check=True
        )
        print("[OK] pip actualizado")
        return True
    except subprocess.CalledProcessError:
        print("[WARN] No se pudo actualizar pip (continuando)")
        return True

def test_imports():
    """Probar importaciones después de la instalación"""
    print("\n[TEST] Probando importaciones...")
    
    imports_to_test = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "uvicorn"),
        ("sqlalchemy", "SQLAlchemy"),
        ("pydantic", "Pydantic"),
        ("requests", "requests"),
        ("aiofiles", "aiofiles"),
        ("jinja2", "Jinja2")
    ]
    
    success_count = 0
    for module, name in imports_to_test:
        try:
            __import__(module)
            print(f"  [OK] {name}")
            success_count += 1
        except ImportError:
            print(f"  [ERROR] {name}")
    
    print(f"\n[INFO] Importaciones: {success_count}/{len(imports_to_test)} exitosas")
    return success_count == len(imports_to_test)

def run_quick_test():
    """Ejecutar el test rápido"""
    print("\n[TEST] Ejecutando test rapido...")
    
    try:
        result = subprocess.run(
            [sys.executable, "test_quick.py"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("[WARN] Warnings:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] Error ejecutando test: {e}")
        return False

def main():
    """Función principal"""
    print_header()
    
    # Verificar Python
    if not check_python_version():
        return 1
    
    # Actualizar pip
    upgrade_pip()
    
    # Intentar instalar desde requirements
    if not install_from_requirements():
        # Si falla, instalar paquetes críticos individualmente
        if not install_critical_packages():
            print("\n[ERROR] No se pudieron instalar todas las dependencias")
            print("[INFO] Intenta ejecutar manualmente:")
            print("   pip install -r edumon/backend/requirements.txt")
            return 1
    
    # Probar importaciones
    if not test_imports():
        print("\n[WARN] Algunas importaciones fallaron")
        print("[INFO] El sistema puede funcionar parcialmente")
    
    # Ejecutar test rápido
    print("\n" + "="*60)
    print("INSTALACION COMPLETADA!")
    print("="*60)
    
    if run_quick_test():
        print("\n[SUCCESS] Todo listo! Ahora puedes ejecutar:")
        print("   python run_server.py")
        print("   INICIAR_SERVIDOR.bat (Windows)")
        print("   ./iniciar_servidor.sh (Linux/Mac)")
        return 0
    else:
        print("\n[WARN] Instalacion completada pero hay algunos problemas")
        print("[INFO] Revisa los errores arriba")
        return 1

if __name__ == "__main__":
    sys.exit(main())