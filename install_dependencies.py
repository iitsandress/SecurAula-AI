#!/usr/bin/env python3
"""
Instalador automático de dependencias para SecurAula-AI / EduMon
"""
import sys
import subprocess
import os
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.WHITE}🔧 INSTALADOR DE DEPENDENCIAS - SecurAula-AI{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")

def check_python_version():
    """Verificar versión de Python"""
    print(f"{Colors.BLUE}🐍 Verificando Python...{Colors.END}")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"{Colors.RED}❌ Python {version.major}.{version.minor} no es compatible{Colors.END}")
        print(f"{Colors.YELLOW}📥 Se requiere Python 3.7 o superior{Colors.END}")
        return False
    
    print(f"{Colors.GREEN}✅ Python {version.major}.{version.minor}.{version.micro} OK{Colors.END}")
    return True

def install_package(package):
    """Instalar un paquete específico"""
    try:
        print(f"  📦 Instalando {package}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"  ✅ {package} instalado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error instalando {package}: {e}")
        return False

def install_from_requirements():
    """Instalar desde archivo requirements"""
    req_file = Path("edumon/backend/requirements.txt")
    
    if not req_file.exists():
        print(f"{Colors.RED}❌ Archivo requirements.txt no encontrado{Colors.END}")
        return False
    
    print(f"{Colors.BLUE}📋 Instalando desde requirements.txt...{Colors.END}")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"{Colors.GREEN}✅ Dependencias del backend instaladas{Colors.END}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Error instalando requirements: {e}{Colors.END}")
        print(f"{Colors.YELLOW}Intentando instalación individual...{Colors.END}")
        return False

def install_critical_packages():
    """Instalar paquetes críticos uno por uno"""
    print(f"{Colors.BLUE}🔧 Instalando paquetes críticos...{Colors.END}")
    
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
    
    print(f"\n{Colors.CYAN}📊 Resultado: {success_count}/{len(critical_packages)} paquetes instalados{Colors.END}")
    return success_count == len(critical_packages)

def upgrade_pip():
    """Actualizar pip"""
    print(f"{Colors.BLUE}⬆️  Actualizando pip...{Colors.END}")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"{Colors.GREEN}✅ pip actualizado{Colors.END}")
        return True
    except subprocess.CalledProcessError:
        print(f"{Colors.YELLOW}⚠️  No se pudo actualizar pip (continuando){Colors.END}")
        return True

def test_imports():
    """Probar importaciones después de la instalación"""
    print(f"\n{Colors.BLUE}🧪 Probando importaciones...{Colors.END}")
    
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
            print(f"  ✅ {name}")
            success_count += 1
        except ImportError:
            print(f"  ❌ {name}")
    
    print(f"\n{Colors.CYAN}📊 Importaciones: {success_count}/{len(imports_to_test)} exitosas{Colors.END}")
    return success_count == len(imports_to_test)

def run_quick_test():
    """Ejecutar el test rápido"""
    print(f"\n{Colors.BLUE}🚀 Ejecutando test rápido...{Colors.END}")
    
    try:
        result = subprocess.run(
            [sys.executable, "test_quick.py"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"{Colors.YELLOW}Warnings:{Colors.END}")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"{Colors.RED}❌ Error ejecutando test: {e}{Colors.END}")
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
            print(f"\n{Colors.RED}❌ No se pudieron instalar todas las dependencias{Colors.END}")
            print(f"{Colors.YELLOW}💡 Intenta ejecutar manualmente:{Colors.END}")
            print(f"   pip install -r edumon/backend/requirements.txt")
            return 1
    
    # Probar importaciones
    if not test_imports():
        print(f"\n{Colors.YELLOW}⚠️  Algunas importaciones fallaron{Colors.END}")
        print(f"{Colors.YELLOW}💡 El sistema puede funcionar parcialmente{Colors.END}")
    
    # Ejecutar test rápido
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.WHITE}🎉 ¡INSTALACIÓN COMPLETADA!{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}")
    
    if run_quick_test():
        print(f"\n{Colors.GREEN}✅ ¡Todo listo! Ahora puedes ejecutar:{Colors.END}")
        print(f"   {Colors.CYAN}python run_server.py{Colors.END}")
        print(f"   {Colors.CYAN}INICIAR_SERVIDOR.bat{Colors.END} (Windows)")
        print(f"   {Colors.CYAN}./iniciar_servidor.sh{Colors.END} (Linux/Mac)")
        return 0
    else:
        print(f"\n{Colors.YELLOW}⚠️  Instalación completada pero hay algunos problemas{Colors.END}")
        print(f"{Colors.YELLOW}💡 Revisa los errores arriba{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())