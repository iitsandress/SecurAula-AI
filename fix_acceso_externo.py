#!/usr/bin/env python3
"""
Fix Acceso Externo - Solución Rápida
Este script corrige la configuración para permitir acceso externo al servidor EduMon
"""
import subprocess
import os
import sys
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
    print(f"{Colors.BOLD}{Colors.WHITE}🔧 FIX ACCESO EXTERNO EDUMON{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.YELLOW}Configurando servidor para acceso externo...{Colors.END}\n")

def stop_current_containers():
    """Para los contenedores actuales"""
    print(f"{Colors.BLUE}🛑 Deteniendo contenedores actuales...{Colors.END}")
    
    try:
        docker_dir = Path("edumon/docker")
        if docker_dir.exists():
            os.chdir(docker_dir)
            result = subprocess.run(["docker", "compose", "down"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Contenedores detenidos{Colors.END}")
                return True
            else:
                print(f"{Colors.YELLOW}⚠️  Error deteniendo contenedores: {result.stderr}{Colors.END}")
                return False
        else:
            print(f"{Colors.RED}❌ Directorio docker no encontrado{Colors.END}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
        return False
    finally:
        try:
            os.chdir("../..")
        except:
            pass

def start_external_containers():
    """Inicia contenedores con configuración externa"""
    print(f"{Colors.BLUE}🚀 Iniciando contenedores con acceso externo...{Colors.END}")
    
    try:
        docker_dir = Path("edumon/docker")
        if docker_dir.exists():
            os.chdir(docker_dir)
            
            # Usar el archivo docker-compose-external.yml
            result = subprocess.run([
                "docker", "compose", 
                "-f", "docker-compose-external.yml", 
                "up", "-d", "--build"
            ], capture_output=False, text=True)
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Contenedores iniciados con acceso externo{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ Error iniciando contenedores{Colors.END}")
                return False
        else:
            print(f"{Colors.RED}❌ Directorio docker no encontrado{Colors.END}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
        return False
    finally:
        try:
            os.chdir("../..")
        except:
            pass

def check_containers_status():
    """Verifica el estado de los contenedores"""
    print(f"\n{Colors.BLUE}📊 Verificando estado de contenedores...{Colors.END}")
    
    try:
        docker_dir = Path("edumon/docker")
        if docker_dir.exists():
            os.chdir(docker_dir)
            result = subprocess.run([
                "docker", "compose", 
                "-f", "docker-compose-external.yml", 
                "ps"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"{Colors.CYAN}Estado de contenedores:{Colors.END}")
                print(result.stdout)
                return True
            else:
                print(f"{Colors.RED}❌ Error verificando contenedores{Colors.END}")
                return False
        else:
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
        return False
    finally:
        try:
            os.chdir("../..")
        except:
            pass

def show_firewall_commands():
    """Muestra comandos para configurar firewall"""
    print(f"\n{Colors.YELLOW}🔥 CONFIGURACIÓN DE FIREWALL REQUERIDA{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    
    print(f"\n{Colors.WHITE}Para Ubuntu/Debian (UFW):{Colors.END}")
    print(f"sudo ufw allow 8000/tcp")
    print(f"sudo ufw allow 8080/tcp")
    print(f"sudo ufw allow 3000/tcp")
    print(f"sudo ufw reload")
    
    print(f"\n{Colors.WHITE}Para CentOS/RHEL/Fedora (firewalld):{Colors.END}")
    print(f"sudo firewall-cmd --permanent --add-port=8000/tcp")
    print(f"sudo firewall-cmd --permanent --add-port=8080/tcp")
    print(f"sudo firewall-cmd --permanent --add-port=3000/tcp")
    print(f"sudo firewall-cmd --reload")
    
    print(f"\n{Colors.WHITE}Para sistemas con iptables:{Colors.END}")
    print(f"sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT")
    print(f"sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT")
    print(f"sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT")
    print(f"sudo iptables-save > /etc/iptables/rules.v4")

def get_local_ip():
    """Obtiene la IP local"""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "No disponible"

def show_access_info():
    """Muestra información de acceso"""
    local_ip = get_local_ip()
    
    print(f"\n{Colors.GREEN}🎉 CONFIGURACIÓN COMPLETADA{Colors.END}")
    print(f"{Colors.CYAN}{'='*40}{Colors.END}")
    
    print(f"\n{Colors.WHITE}URLs de acceso local:{Colors.END}")
    if local_ip != "No disponible":
        print(f"📊 Dashboard: http://{local_ip}:8000/dashboard?api_key=S1R4X")
        print(f"❤️  Health: http://{local_ip}:8000/health")
        print(f"🗄️  pgAdmin: http://{local_ip}:8080")
        print(f"📈 Metabase: http://{local_ip}:3000")
    
    print(f"\n{Colors.WHITE}URLs de acceso externo (después de configurar firewall/router):{Colors.END}")
    print(f"📊 Dashboard: http://[tu_ip_publica]:8000/dashboard?api_key=S1R4X")
    print(f"❤️  Health: http://[tu_ip_publica]:8000/health")
    print(f"🗄️  pgAdmin: http://[tu_ip_publica]:8080")
    print(f"📈 Metabase: http://[tu_ip_publica]:3000")
    
    print(f"\n{Colors.YELLOW}⚠️  IMPORTANTE:{Colors.END}")
    print(f"1. Configura el firewall con los comandos mostrados arriba")
    print(f"2. Si estás detrás de un router, configura port forwarding")
    print(f"3. Verifica que tu proveedor de internet no bloquee estos puertos")

def create_management_script():
    """Crea script de gestión"""
    script_content = '''#!/bin/bash
# Script de gestión para EduMon con acceso externo

DOCKER_DIR="edumon/docker"
COMPOSE_FILE="docker-compose-external.yml"

case "$1" in
    start)
        echo "🚀 Iniciando EduMon con acceso externo..."
        cd $DOCKER_DIR
        docker compose -f $COMPOSE_FILE up -d
        ;;
    stop)
        echo "🛑 Deteniendo EduMon..."
        cd $DOCKER_DIR
        docker compose -f $COMPOSE_FILE down
        ;;
    restart)
        echo "🔄 Reiniciando EduMon..."
        cd $DOCKER_DIR
        docker compose -f $COMPOSE_FILE down
        docker compose -f $COMPOSE_FILE up -d
        ;;
    status)
        echo "📊 Estado de EduMon:"
        cd $DOCKER_DIR
        docker compose -f $COMPOSE_FILE ps
        ;;
    logs)
        echo "📋 Logs de EduMon:"
        cd $DOCKER_DIR
        docker compose -f $COMPOSE_FILE logs -f
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
'''
    
    try:
        with open("manage_edumon.sh", "w") as f:
            f.write(script_content)
        
        # Hacer ejecutable
        os.chmod("manage_edumon.sh", 0o755)
        
        print(f"{Colors.GREEN}✅ Script de gestión creado: manage_edumon.sh{Colors.END}")
        print(f"{Colors.CYAN}Uso: ./manage_edumon.sh [start|stop|restart|status|logs]{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  No se pudo crear script de gestión: {e}{Colors.END}")

def main():
    print_header()
    
    # Paso 1: Detener contenedores actuales
    if not stop_current_containers():
        print(f"{Colors.RED}❌ No se pudieron detener los contenedores actuales{Colors.END}")
        return 1
    
    # Paso 2: Iniciar con configuración externa
    if not start_external_containers():
        print(f"{Colors.RED}❌ No se pudieron iniciar los contenedores con acceso externo{Colors.END}")
        return 1
    
    # Paso 3: Verificar estado
    check_containers_status()
    
    # Paso 4: Mostrar comandos de firewall
    show_firewall_commands()
    
    # Paso 5: Crear script de gestión
    create_management_script()
    
    # Paso 6: Mostrar información de acceso
    show_access_info()
    
    print(f"\n{Colors.CYAN}📋 PRÓXIMOS PASOS:{Colors.END}")
    print(f"1. Ejecutar comandos de firewall mostrados arriba")
    print(f"2. Configurar port forwarding en router (si es necesario)")
    print(f"3. Probar acceso desde otra máquina")
    print(f"4. Usar ./manage_edumon.sh para gestionar el servidor")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Operación cancelada{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error inesperado: {e}{Colors.END}")
        sys.exit(1)