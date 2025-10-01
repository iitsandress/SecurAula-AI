#!/usr/bin/env python3
"""
Diagnóstico de Servidor EduMon - Acceso Externo
Este script diagnostica problemas de conectividad externa al servidor Docker
"""
import subprocess
import socket
import requests
import json
import os
import platform
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
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.WHITE}🔍 DIAGNÓSTICO DE SERVIDOR EDUMON{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.YELLOW}Diagnosticando problemas de acceso externo...{Colors.END}\n")

def get_local_ip():
    """Obtiene la IP local de la máquina"""
    try:
        # Conectar a un servidor externo para obtener la IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "No disponible"

def check_docker_status():
    """Verifica el estado de Docker y contenedores"""
    print(f"{Colors.BLUE}🐳 Verificando estado de Docker...{Colors.END}")
    
    try:
        # Verificar si Docker está corriendo
        result = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"{Colors.RED}❌ Docker no está corriendo{Colors.END}")
            return False
        
        print(f"{Colors.GREEN}✅ Docker está corriendo{Colors.END}")
        
        # Verificar contenedores de EduMon
        docker_dir = Path("edumon/docker")
        if docker_dir.exists():
            os.chdir(docker_dir)
            result = subprocess.run(["docker", "compose", "ps"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{Colors.CYAN}📊 Estado de contenedores:{Colors.END}")
                print(result.stdout)
                
                # Verificar si el backend está corriendo
                if "backend" in result.stdout and "Up" in result.stdout:
                    print(f"{Colors.GREEN}✅ Contenedor backend está corriendo{Colors.END}")
                    return True
                else:
                    print(f"{Colors.RED}❌ Contenedor backend no está corriendo{Colors.END}")
                    return False
            os.chdir("../..")
        else:
            print(f"{Colors.YELLOW}⚠️  Directorio docker no encontrado{Colors.END}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}❌ Error verificando Docker: {e}{Colors.END}")
        return False

def test_local_connectivity():
    """Prueba conectividad local"""
    print(f"\n{Colors.BLUE}🔍 Probando conectividad local...{Colors.END}")
    
    endpoints = [
        ("http://localhost:8000/health", "Backend (localhost)"),
        ("http://127.0.0.1:8000/health", "Backend (127.0.0.1)"),
        ("http://0.0.0.0:8000/health", "Backend (0.0.0.0)"),
    ]
    
    local_ip = get_local_ip()
    if local_ip != "No disponible":
        endpoints.append((f"http://{local_ip}:8000/health", f"Backend (IP local: {local_ip})"))
    
    working_endpoints = []
    
    for url, description in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"{Colors.GREEN}✅ {description}: OK{Colors.END}")
                working_endpoints.append(url)
            else:
                print(f"{Colors.YELLOW}⚠️  {description}: HTTP {response.status_code}{Colors.END}")
        except requests.exceptions.ConnectionError:
            print(f"{Colors.RED}❌ {description}: No conecta{Colors.END}")
        except requests.exceptions.Timeout:
            print(f"{Colors.RED}❌ {description}: Timeout{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ {description}: Error - {e}{Colors.END}")
    
    return working_endpoints

def check_port_binding():
    """Verifica cómo están configurados los puertos"""
    print(f"\n{Colors.BLUE}🔌 Verificando configuración de puertos...{Colors.END}")
    
    try:
        # Verificar puertos abiertos
        result = subprocess.run(["netstat", "-tlnp"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            port_8000_found = False
            
            for line in lines:
                if ":8000" in line:
                    print(f"{Colors.CYAN}📍 Puerto 8000: {line.strip()}{Colors.END}")
                    port_8000_found = True
                    
                    if "0.0.0.0:8000" in line:
                        print(f"{Colors.GREEN}✅ Puerto 8000 está escuchando en todas las interfaces (0.0.0.0){Colors.END}")
                    elif "127.0.0.1:8000" in line:
                        print(f"{Colors.YELLOW}⚠️  Puerto 8000 solo escucha en localhost (127.0.0.1){Colors.END}")
                        print(f"{Colors.YELLOW}   Esto impide el acceso externo{Colors.END}")
            
            if not port_8000_found:
                print(f"{Colors.RED}❌ Puerto 8000 no está abierto{Colors.END}")
                
        else:
            # Intentar con ss si netstat no funciona
            result = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{Colors.CYAN}📍 Puertos abiertos (ss):{Colors.END}")
                for line in result.stdout.split('\n'):
                    if ":8000" in line:
                        print(f"   {line.strip()}")
            else:
                print(f"{Colors.YELLOW}⚠️  No se pudo verificar puertos (netstat/ss no disponible){Colors.END}")
                
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Error verificando puertos: {e}{Colors.END}")

def check_firewall():
    """Verifica configuración de firewall"""
    print(f"\n{Colors.BLUE}🔥 Verificando firewall...{Colors.END}")
    
    system = platform.system().lower()
    
    if system == "linux":
        # Verificar iptables
        try:
            result = subprocess.run(["iptables", "-L", "-n"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{Colors.CYAN}📋 Reglas de iptables activas{Colors.END}")
                # Buscar reglas que puedan bloquear el puerto 8000
                if "8000" in result.stdout:
                    print(f"{Colors.YELLOW}⚠️  Encontradas reglas para puerto 8000{Colors.END}")
                else:
                    print(f"{Colors.GREEN}✅ No hay reglas específicas para puerto 8000{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  No se pudo verificar iptables (permisos?){Colors.END}")
        except FileNotFoundError:
            print(f"{Colors.YELLOW}⚠️  iptables no disponible{Colors.END}")
        
        # Verificar ufw
        try:
            result = subprocess.run(["ufw", "status"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{Colors.CYAN}📋 Estado de UFW:{Colors.END}")
                print(f"   {result.stdout.strip()}")
            else:
                print(f"{Colors.YELLOW}⚠️  UFW no disponible{Colors.END}")
        except FileNotFoundError:
            print(f"{Colors.YELLOW}⚠️  UFW no instalado{Colors.END}")
            
    elif system == "windows":
        print(f"{Colors.CYAN}📋 Sistema Windows detectado{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  Verificar Windows Firewall manualmente{Colors.END}")
        print(f"   Panel de Control > Sistema y Seguridad > Firewall de Windows Defender")
        
    else:
        print(f"{Colors.YELLOW}⚠️  Sistema {system} - verificar firewall manualmente{Colors.END}")

def show_solutions():
    """Muestra soluciones para problemas comunes"""
    print(f"\n{Colors.CYAN}🔧 SOLUCIONES PARA ACCESO EXTERNO{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    
    print(f"\n{Colors.YELLOW}1. Problema: Puerto solo escucha en localhost{Colors.END}")
    print(f"   {Colors.WHITE}Solución:{Colors.END} Modificar docker-compose.yml")
    print(f"   Cambiar: {Colors.RED}ports: - \"8000:8000\"{Colors.END}")
    print(f"   Por:     {Colors.GREEN}ports: - \"0.0.0.0:8000:8000\"{Colors.END}")
    
    print(f"\n{Colors.YELLOW}2. Problema: Firewall bloqueando puerto{Colors.END}")
    print(f"   {Colors.WHITE}Linux (UFW):{Colors.END}")
    print(f"   sudo ufw allow 8000")
    print(f"   {Colors.WHITE}Linux (iptables):{Colors.END}")
    print(f"   sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT")
    print(f"   {Colors.WHITE}Windows:{Colors.END}")
    print(f"   Abrir Windows Firewall > Regla de entrada > Puerto 8000")
    
    print(f"\n{Colors.YELLOW}3. Problema: Router/NAT{Colors.END}")
    print(f"   {Colors.WHITE}Solución:{Colors.END} Configurar port forwarding en router")
    print(f"   Puerto externo: 8000 → IP interna: [tu_ip_local]:8000")
    
    print(f"\n{Colors.YELLOW}4. Problema: Docker no expone correctamente{Colors.END}")
    print(f"   {Colors.WHITE}Reiniciar contenedores:{Colors.END}")
    print(f"   cd edumon/docker")
    print(f"   docker compose down")
    print(f"   docker compose up -d")

def create_fixed_docker_compose():
    """Crea una versión corregida del docker-compose.yml"""
    print(f"\n{Colors.BLUE}🔧 Creando docker-compose.yml corregido...{Colors.END}")
    
    try:
        # Leer el archivo actual
        with open("edumon/docker/docker-compose.yml", "r") as f:
            content = f.read()
        
        # Hacer backup
        with open("edumon/docker/docker-compose.yml.backup", "w") as f:
            f.write(content)
        
        # Corregir binding de puertos
        content = content.replace('- "8000:8000"', '- "0.0.0.0:8000:8000"')
        content = content.replace('- "8080:80"', '- "0.0.0.0:8080:80"')
        content = content.replace('- "3000:3000"', '- "0.0.0.0:3000:3000"')
        
        # Guardar versión corregida
        with open("edumon/docker/docker-compose-fixed.yml", "w") as f:
            f.write(content)
        
        print(f"{Colors.GREEN}✅ Archivo corregido creado: edumon/docker/docker-compose-fixed.yml{Colors.END}")
        print(f"{Colors.CYAN}📋 Para usar la versión corregida:{Colors.END}")
        print(f"   cd edumon/docker")
        print(f"   docker compose -f docker-compose-fixed.yml down")
        print(f"   docker compose -f docker-compose-fixed.yml up -d")
        
        return True
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error creando archivo corregido: {e}{Colors.END}")
        return False

def main():
    print_header()
    
    # Obtener IP local
    local_ip = get_local_ip()
    print(f"{Colors.CYAN}📍 IP local detectada: {local_ip}{Colors.END}")
    
    # Verificar Docker
    docker_ok = check_docker_status()
    
    # Probar conectividad local
    working_endpoints = test_local_connectivity()
    
    # Verificar puertos
    check_port_binding()
    
    # Verificar firewall
    check_firewall()
    
    # Mostrar soluciones
    show_solutions()
    
    # Crear archivo corregido
    create_fixed_docker_compose()
    
    # Resumen final
    print(f"\n{Colors.CYAN}📋 RESUMEN DEL DIAGNÓSTICO{Colors.END}")
    print(f"{Colors.CYAN}{'='*40}{Colors.END}")
    
    if working_endpoints:
        print(f"{Colors.GREEN}✅ Servidor funciona localmente{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  Problema: Acceso externo bloqueado{Colors.END}")
        print(f"\n{Colors.WHITE}Pasos recomendados:{Colors.END}")
        print(f"1. Usar docker-compose-fixed.yml")
        print(f"2. Configurar firewall para puerto 8000")
        print(f"3. Verificar configuración de router/NAT")
    else:
        print(f"{Colors.RED}❌ Servidor no responde localmente{Colors.END}")
        print(f"\n{Colors.WHITE}Pasos recomendados:{Colors.END}")
        print(f"1. Verificar que Docker esté corriendo")
        print(f"2. Reiniciar contenedores")
        print(f"3. Revisar logs: docker compose logs backend")
    
    print(f"\n{Colors.CYAN}🌐 URLs para probar después de la corrección:{Colors.END}")
    if local_ip != "No disponible":
        print(f"   Local: http://{local_ip}:8000/dashboard?api_key=S1R4X")
    print(f"   Externa: http://[tu_ip_publica]:8000/dashboard?api_key=S1R4X")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Diagnóstico cancelado{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error en diagnóstico: {e}{Colors.END}")