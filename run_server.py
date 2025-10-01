#!/usr/bin/env python3
"""
EduMon Server Runner - Versión Automatizada Completa

Este script automatiza completamente el levantamiento del servidor EduMon:
- Verifica Docker
- Construye y levanta contenedores
- Verifica conectividad
- Proporciona URLs de acceso
- Maneja errores automáticamente

Un solo click para tener todo funcionando.
"""
import sys
import subprocess
import os
import time
import json
import platform
import shutil
from pathlib import Path

class Colors:
    """Colores para terminal"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Imprime el header del programa"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.WHITE}🎓 SECURAAULA-AI / EDUMON - SERVIDOR AUTOMATIZADO{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.YELLOW}🚀 Iniciando servidor completo con Docker...{Colors.END}\n")

def check_docker():
    """Verifica si Docker está instalado y corriendo"""
    print(f"{Colors.BLUE}🐳 Verificando Docker...{Colors.END}")
    
    # Verificar si Docker está instalado
    if not shutil.which("docker"):
        print(f"{Colors.RED}❌ Docker no está instalado.{Colors.END}")
        print(f"{Colors.YELLOW}📥 Por favor instala Docker Desktop desde: https://www.docker.com/products/docker-desktop{Colors.END}")
        return False
    
    # Verificar si Docker está corriendo
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"{Colors.RED}❌ Docker no está corriendo.{Colors.END}")
            print(f"{Colors.YELLOW}🔄 Por favor inicia Docker Desktop y vuelve a ejecutar este script.{Colors.END}")
            return False
        
        print(f"{Colors.GREEN}✅ Docker está instalado y corriendo{Colors.END}")
        return True
        
    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}❌ Docker no responde (timeout).{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Error verificando Docker: {e}{Colors.END}")
        return False

def check_docker_compose():
    """Verifica si Docker Compose está disponible"""
    print(f"{Colors.BLUE}🔧 Verificando Docker Compose...{Colors.END}")
    
    # Probar docker compose (nuevo)
    try:
        result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ Docker Compose disponible{Colors.END}")
            return "docker compose"
    except:
        pass
    
    # Probar docker-compose (legacy)
    try:
        result = subprocess.run(["docker-compose", "version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ Docker Compose (legacy) disponible{Colors.END}")
            return "docker-compose"
    except:
        pass
    
    print(f"{Colors.RED}❌ Docker Compose no está disponible{Colors.END}")
    return None

def stop_existing_containers():
    """Para contenedores existentes si están corriendo"""
    print(f"{Colors.BLUE}🛑 Verificando contenedores existentes...{Colors.END}")
    
    docker_dir = Path("edumon/docker")
    if not docker_dir.exists():
        print(f"{Colors.RED}❌ Directorio docker no encontrado: {docker_dir}{Colors.END}")
        return False
    
    try:
        os.chdir(docker_dir)
        
        # Verificar si hay contenedores corriendo
        result = subprocess.run(["docker", "compose", "ps", "-q"], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"{Colors.YELLOW}⚠️  Deteniendo contenedores existentes...{Colors.END}")
            subprocess.run(["docker", "compose", "down"], check=True)
            print(f"{Colors.GREEN}✅ Contenedores detenidos{Colors.END}")
        else:
            print(f"{Colors.GREEN}✅ No hay contenedores corriendo{Colors.END}")
        
        return True
        
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Error deteniendo contenedores: {e}{Colors.END}")
        return True  # Continuar de todas formas
    finally:
        os.chdir("../..")

def verify_docker_files():
    """Verifica que existan los archivos de Docker necesarios"""
    print(f"{Colors.BLUE}📁 Verificando archivos de Docker...{Colors.END}")
    
    required_files = [
        "edumon/docker/docker-compose.yml",
        "edumon/docker/.env",
        "edumon/docker/Dockerfile.backend",
        "edumon/backend/requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"{Colors.RED}❌ Archivos faltantes:{Colors.END}")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print(f"{Colors.GREEN}✅ Todos los archivos de Docker están presentes{Colors.END}")
    return True

def build_and_start_containers():
    """Construye y levanta los contenedores"""
    print(f"{Colors.BLUE}🏗️  Construyendo y levantando contenedores...{Colors.END}")
    print(f"{Colors.YELLOW}⏳ Esto puede tomar varios minutos la primera vez...{Colors.END}")
    
    docker_dir = Path("edumon/docker")
    
    try:
        os.chdir(docker_dir)
        
        # Construir y levantar contenedores
        print(f"{Colors.CYAN}🔨 Construyendo imágenes...{Colors.END}")
        result = subprocess.run(
            ["docker", "compose", "up", "-d", "--build"],
            capture_output=False,  # Mostrar output en tiempo real
            text=True
        )
        
        if result.returncode != 0:
            print(f"{Colors.RED}❌ Error construyendo contenedores{Colors.END}")
            return False
        
        print(f"{Colors.GREEN}✅ Contenedores construidos y levantados{Colors.END}")
        return True
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error en construcción: {e}{Colors.END}")
        return False
    finally:
        os.chdir("../..")

def wait_for_services():
    """Espera a que los servicios estén listos"""
    print(f"{Colors.BLUE}⏳ Esperando a que los servicios estén listos...{Colors.END}")
    
    services = {
        "PostgreSQL": ("localhost", 5432),
        "Backend": ("0.0.0.0", 8000),
        "pgAdmin": ("0.0.0.0", 8080),
        "Metabase": ("0.0.0.0", 3000)
    }
    
    max_wait = 120  # 2 minutos máximo
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        all_ready = True
        
        for service_name, (host, port) in services.items():
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result != 0:
                    all_ready = False
                    break
                    
            except Exception:
                all_ready = False
                break
        
        if all_ready:
            print(f"{Colors.GREEN}✅ Todos los servicios están listos{Colors.END}")
            return True
        
        print(f"{Colors.YELLOW}⏳ Esperando servicios... ({int(time.time() - start_time)}s){Colors.END}")
        time.sleep(5)
    
    print(f"{Colors.YELLOW}⚠️  Algunos servicios pueden no estar listos aún{Colors.END}")
    return True

def verify_backend_health():
    """Verifica que el backend responda correctamente"""
    print(f"{Colors.BLUE}🏥 Verificando salud del backend...{Colors.END}")
    
    try:
        import requests
        
        # Intentar conectar al health endpoint
        for attempt in range(6):  # 30 segundos máximo
            try:
                response = requests.get("http://0.0.0.0:8000/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"{Colors.GREEN}✅ Backend respondiendo correctamente{Colors.END}")
                    print(f"   📊 Versión: {data.get('version', 'N/A')}")
                    print(f"   🔑 API Key configurada: {data.get('api_key_configured', False)}")
                    return True
            except:
                pass
            
            if attempt < 5:
                print(f"{Colors.YELLOW}⏳ Esperando backend... (intento {attempt + 1}/6){Colors.END}")
                time.sleep(5)
        
        print(f"{Colors.YELLOW}⚠️  Backend no responde, pero puede estar iniciando{Colors.END}")
        return True
        
    except ImportError:
        print(f"{Colors.YELLOW}⚠️  requests no disponible, saltando verificación{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Error verificando backend: {e}{Colors.END}")
        return True

def show_access_info():
    """Muestra información de acceso"""
    print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.WHITE}🎉 ¡SERVIDOR EDUMON LISTO!{Colors.END}")
    print(f"{Colors.GREEN}{'='*70}{Colors.END}")
    
    print(f"\n{Colors.CYAN}🌐 URLs de Acceso:{Colors.END}")
    print(f"   {Colors.WHITE}📊 Dashboard Principal:{Colors.END} {Colors.BLUE}http://0.0.0.0:8000/dashboard?api_key=S1R4X{Colors.END}")
    print(f"   {Colors.WHITE}📖 Documentación API:{Colors.END} {Colors.BLUE}http://0.0.0.0:8000/docs{Colors.END}")
    print(f"   {Colors.WHITE}❤️  Estado del Servidor:{Colors.END} {Colors.BLUE}http://0.0.0.0:8000/health{Colors.END}")
    print(f"   {Colors.WHITE}🗄️  pgAdmin (Base de Datos):{Colors.END} {Colors.BLUE}http://0.0.0.0:8080{Colors.END}")
    print(f"   {Colors.WHITE}📈 Metabase (Analytics):{Colors.END} {Colors.BLUE}http://0.0.0.0:3000{Colors.END}")
    
    print(f"\n{Colors.CYAN}🔑 Credenciales:{Colors.END}")
    print(f"   {Colors.WHITE}API Key:{Colors.END} {Colors.YELLOW}S1R4X{Colors.END}")
    print(f"   {Colors.WHITE}pgAdmin:{Colors.END} {Colors.YELLOW}admin@edumon.com / admin123{Colors.END}")
    print(f"   {Colors.WHITE}PostgreSQL:{Colors.END} {Colors.YELLOW}edumon / edumon123{Colors.END}")
    
    print(f"\n{Colors.CYAN}🤖 Para Agentes Estudiantes:{Colors.END}")
    print(f"   {Colors.WHITE}URL del Servidor:{Colors.END} {Colors.YELLOW}http://<tu-ip>:8000{Colors.END}")
    print(f"   {Colors.WHITE}API Key:{Colors.END} {Colors.YELLOW}S1R4X{Colors.END}")
    
    print(f"\n{Colors.CYAN}🛠️  Comandos Útiles:{Colors.END}")
    print(f"   {Colors.WHITE}Ver logs:{Colors.END} {Colors.YELLOW}cd edumon/docker && docker compose logs -f{Colors.END}")
    print(f"   {Colors.WHITE}Parar servidor:{Colors.END} {Colors.YELLOW}cd edumon/docker && docker compose down{Colors.END}")
    print(f"   {Colors.WHITE}Reiniciar:{Colors.END} {Colors.YELLOW}cd edumon/docker && docker compose restart{Colors.END}")
    
    print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")

def show_container_status():
    """Muestra el estado de los contenedores"""
    print(f"\n{Colors.BLUE}📊 Estado de Contenedores:{Colors.END}")
    
    try:
        docker_dir = Path("edumon/docker")
        os.chdir(docker_dir)
        
        result = subprocess.run(["docker", "compose", "ps"], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"{Colors.YELLOW}⚠️  No se pudo obtener el estado de contenedores{Colors.END}")
            
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Error obteniendo estado: {e}{Colors.END}")
    finally:
        try:
            os.chdir("../..")
        except:
            pass

def main():
    """Función principal"""
    try:
        print_header()
        
        # Verificar Docker
        if not check_docker():
            return 1
        
        # Verificar Docker Compose
        compose_cmd = check_docker_compose()
        if not compose_cmd:
            return 1
        
        # Verificar archivos necesarios
        if not verify_docker_files():
            return 1
        
        # Parar contenedores existentes
        stop_existing_containers()
        
        # Construir y levantar contenedores
        if not build_and_start_containers():
            return 1
        
        # Esperar a que los servicios estén listos
        wait_for_services()
        
        # Verificar salud del backend
        verify_backend_health()
        
        # Mostrar estado de contenedores
        show_container_status()
        
        # Mostrar información de acceso
        show_access_info()
        
        # Mantener el script corriendo para mostrar logs
        print(f"\n{Colors.CYAN}📋 Presiona Ctrl+C para ver opciones de gestión...{Colors.END}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}🛠️  Opciones de Gestión:{Colors.END}")
            print(f"   {Colors.WHITE}1.{Colors.END} Ver logs en tiempo real")
            print(f"   {Colors.WHITE}2.{Colors.END} Parar servidor")
            print(f"   {Colors.WHITE}3.{Colors.END} Reiniciar servidor")
            print(f"   {Colors.WHITE}4.{Colors.END} Salir (dejar servidor corriendo)")
            
            choice = input(f"\n{Colors.CYAN}Selecciona una opción (1-4): {Colors.END}")
            
            if choice == "1":
                print(f"{Colors.CYAN}📋 Mostrando logs (Ctrl+C para salir)...{Colors.END}")
                try:
                    os.chdir("edumon/docker")
                    subprocess.run(["docker", "compose", "logs", "-f"])
                except KeyboardInterrupt:
                    pass
                finally:
                    os.chdir("../..")
            elif choice == "2":
                print(f"{Colors.YELLOW}🛑 Parando servidor...{Colors.END}")
                try:
                    os.chdir("edumon/docker")
                    subprocess.run(["docker", "compose", "down"])
                    print(f"{Colors.GREEN}✅ Servidor detenido{Colors.END}")
                finally:
                    os.chdir("../..")
                return 0
            elif choice == "3":
                print(f"{Colors.YELLOW}🔄 Reiniciando servidor...{Colors.END}")
                try:
                    os.chdir("edumon/docker")
                    subprocess.run(["docker", "compose", "restart"])
                    print(f"{Colors.GREEN}✅ Servidor reiniciado{Colors.END}")
                finally:
                    os.chdir("../..")
            elif choice == "4":
                print(f"{Colors.GREEN}✅ Servidor sigue corriendo en segundo plano{Colors.END}")
                return 0
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Operación cancelada por el usuario{Colors.END}")
        return 0
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error inesperado: {e}{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())