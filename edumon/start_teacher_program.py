#!/usr/bin/env python3
"""
EduMon - Programa del Profesor
Script de inicio para el servidor de monitoreo educativo
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Mostrar banner de inicio"""
    banner = """
 ███████╗██████╗ ██╗   ██╗███╗   ███╗ ██████╗ ███╗   ██╗
 ██╔════╝██╔══██╗██║   ██║████╗ ████║██╔═══██╗████╗  ██║
 █████╗  ██║  ██║██║   ██║██╔████╔██║██║   ██║██╔██╗ ██║
 ██╔══╝  ██║  ██║██║   ██║██║╚██╔╝██║██║   ██║██║╚██╗██║
 ███████╗██████╔╝╚██████╔╝██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
 ╚══════╝╚═════╝  ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝

                    PROGRAMA DEL PROFESOR
 ================================================================
"""
    print(banner)

def check_dependencies():
    """Verificar e instalar dependencias"""
    print("[INFO] Verificando dependencias...")
    
    required_packages = ['fastapi', 'uvicorn', 'pydantic']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"[WARN] Instalando dependencias faltantes: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("[OK] Dependencias instaladas correctamente")
        except subprocess.CalledProcessError:
            print("[ERROR] No se pudieron instalar las dependencias")
            return False
    else:
        print("[OK] Todas las dependencias están disponibles")
    
    return True

def main():
    """Función principal"""
    print_banner()
    
    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Configurar variables de entorno
    os.environ["EDUMON_API_KEY"] = "S1R4X"
    os.environ["PYTHONPATH"] = str(script_dir)
    
    print(f"[INFO] Directorio de trabajo: {os.getcwd()}")
    print(f"[INFO] API Key configurada: {os.environ.get('EDUMON_API_KEY')}")
    
    # Verificar dependencias
    if not check_dependencies():
        print("[ERROR] No se pueden satisfacer las dependencias")
        input("Presiona Enter para salir...")
        return 1
    
    # Cambiar al directorio del servidor
    server_dir = script_dir / "edumon" / "server"
    if not server_dir.exists():
        print(f"[ERROR] Directorio del servidor no encontrado: {server_dir}")
        input("Presiona Enter para salir...")
        return 1
    
    os.chdir(server_dir)
    print(f"[INFO] Cambiando al directorio del servidor: {server_dir}")
    
    # Mostrar información del servidor
    print("\n" + "="*64)
    print("                      SERVIDOR INICIADO")
    print("="*64)
    print()
    print("  📊 Dashboard del Profesor: http://localhost:8000/dashboard")
    print("  🔧 Documentación API:      http://localhost:8000/docs")
    print("  ❤️  Estado del servidor:   http://localhost:8000/health")
    print(f"  🔑 API Key configurada:    {os.environ.get('EDUMON_API_KEY')}")
    print()
    print("  💡 INSTRUCCIONES:")
    print("  1. Abre el dashboard en tu navegador")
    print("  2. Los estudiantes deben ejecutar el agente")
    print("  3. Monitorea las métricas en tiempo real")
    print()
    print("  ⚠️  Presiona Ctrl+C para detener el servidor")
    print("="*64)
    print()
    
    try:
        # Importar la aplicación
        sys.path.insert(0, str(server_dir))
        
        # Ejecutar el servidor
        import uvicorn
        from main import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"[ERROR] Error de importación: {e}")
        print("[INFO] Intentando ejecutar con uvicorn desde línea de comandos...")
        
        try:
            subprocess.run([
                sys.executable, "-m", "uvicorn",
                "main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ])
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"[ERROR] No se pudo ejecutar el servidor: {e}")
            return 1
            
    except KeyboardInterrupt:
        print("\n[INFO] Servidor detenido por el usuario")
        
    except Exception as e:
        print(f"[ERROR] Error ejecutando el servidor: {e}")
        return 1
    
    print("\n[INFO] Programa terminado")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[INFO] Programa interrumpido")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        input("Presiona Enter para salir...")
        sys.exit(1)