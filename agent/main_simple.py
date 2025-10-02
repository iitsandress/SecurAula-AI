#!/usr/bin/env python3
"""
EduMon Agent - Versión Simplificada
Agente educativo sin dependencias de GUI
"""
import os
import sys
import json
import time
import uuid
import socket
import getpass
import requests
import psutil
from datetime import datetime
from typing import Dict, Any, Optional

# Configuración por defecto
DEFAULT_CONFIG = {
    "server_url": "http://190.84.119.196:8000",
    "api_key": "S1R4X",
    "classroom_id": "Aula-1",
    "heartbeat_seconds": 15,
    "collect_disk_metrics": True,
    "collect_network_metrics": True,
    "collect_process_metrics": True,
    "verify_ssl": False,
    "timeout_seconds": 10
}

class SimpleAgent:
    """Agente simple sin GUI"""
    
    def __init__(self):
        self.config = self.load_config()
        self.device_id = self.get_device_id()
        self.session_id = None
        self.running = False
        
        # Configurar requests
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.config['api_key'],
            'Content-Type': 'application/json',
            'User-Agent': 'EduMon-Agent-Simple/2.0.0'
        })
        
        if not self.config.get('verify_ssl', True):
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración"""
        config_file = "config.json"
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Combinar con valores por defecto
                result = DEFAULT_CONFIG.copy()
                result.update(config)
                return result
            except Exception as e:
                print(f"Error cargando configuración: {e}")
        
        # Crear configuración por defecto
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
            print("✅ Configuración creada con valores por defecto")
        except Exception as e:
            print(f"⚠️  No se pudo crear configuración: {e}")
        
        return DEFAULT_CONFIG.copy()
    
    def get_device_id(self) -> str:
        """Obtener ID único del dispositivo"""
        device_file = "device_id.txt"
        
        if os.path.exists(device_file):
            try:
                with open(device_file, 'r') as f:
                    return f.read().strip()
            except:
                pass
        
        # Generar nuevo ID
        device_id = str(uuid.uuid4())
        try:
            with open(device_file, 'w') as f:
                f.write(device_id)
        except:
            pass
        
        return device_id
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Recopilar métricas del sistema"""
        try:
            # Métricas básicas
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            
            metrics = {
                "cpu_percent": round(cpu_percent, 1),
                "mem_percent": round(memory.percent, 1),
                "uptime_seconds": int(uptime)
            }
            
            # Métricas adicionales si están habilitadas
            if self.config.get('collect_disk_metrics', True):
                disk = psutil.disk_usage('/')
                metrics["disk_percent"] = round(disk.percent, 1)
            
            if self.config.get('collect_network_metrics', True):
                net_io = psutil.net_io_counters()
                metrics["network_sent"] = net_io.bytes_sent
                metrics["network_recv"] = net_io.bytes_recv
            
            if self.config.get('collect_process_metrics', True):
                metrics["process_count"] = len(psutil.pids())
            
            return metrics
            
        except Exception as e:
            print(f"Error recopilando métricas: {e}")
            return {
                "cpu_percent": 0.0,
                "mem_percent": 0.0,
                "uptime_seconds": 0
            }
    
    def get_consent(self) -> bool:
        """Solicitar consentimiento del usuario"""
        print("\\n" + "="*60)
        print("🎓 EDUMON - CONSENTIMIENTO PARA MONITOREO EDUCATIVO")
        print("="*60)
        print("\\nEste agente enviará ÚNICAMENTE los siguientes datos:")
        print("✅ Identificador del equipo (anónimo)")
        print("✅ Nombre del host y usuario del sistema")
        print("✅ Métricas de rendimiento: CPU, RAM, disco, red")
        print("✅ Tiempo de actividad del sistema")
        print("✅ Información de procesos (solo nombres)")
        print("\\n❌ NUNCA se capturan:")
        print("❌ Capturas de pantalla")
        print("❌ Pulsaciones de teclado")
        print("❌ Contenido de archivos")
        print("❌ Historial de navegación")
        print("❌ Datos personales")
        print("\\n🛑 Puedes detener el monitoreo en cualquier momento con Ctrl+C")
        print("="*60)
        
        while True:
            response = input("\\n¿Acepta participar en esta sesión de monitoreo? (si/no): ").strip().lower()
            if response in ['si', 'sí', 's', 'yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            else:
                print("Por favor responda 'si' o 'no'")
    
    def register_with_server(self) -> bool:
        """Registrarse con el servidor"""
        try:
            payload = {
                "device_id": self.device_id,
                "hostname": socket.gethostname(),
                "username": getpass.getuser(),
                "consent": True,
                "classroom_id": self.config.get('classroom_id')
            }
            
            print(f"🔗 Conectando con servidor: {self.config['server_url']}")
            
            response = self.session.post(
                f"{self.config['server_url']}/api/v1/register",
                json=payload,
                timeout=self.config.get('timeout_seconds', 10)
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data["session_id"]
                print(f"✅ Registro exitoso. Session ID: {self.session_id}")
                return True
            else:
                print(f"❌ Error en registro: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error conectando con servidor: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """Enviar heartbeat con métricas"""
        try:
            if not self.session_id:
                return False
            
            metrics = self.get_system_metrics()
            
            payload = {
                "device_id": self.device_id,
                "session_id": self.session_id,
                "metrics": metrics
            }
            
            response = self.session.post(
                f"{self.config['server_url']}/api/v1/heartbeat",
                json=payload,
                timeout=self.config.get('timeout_seconds', 10)
            )
            
            if response.status_code == 200:
                print(f"📊 Métricas enviadas - CPU: {metrics['cpu_percent']}% RAM: {metrics['mem_percent']}%")
                return True
            else:
                print(f"⚠️  Error enviando métricas: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en heartbeat: {e}")
            return False
    
    def unregister_from_server(self, reason: str = "user_request") -> bool:
        """Desregistrarse del servidor"""
        try:
            if not self.session_id:
                return True
            
            payload = {
                "device_id": self.device_id,
                "session_id": self.session_id,
                "reason": reason
            }
            
            response = self.session.post(
                f"{self.config['server_url']}/api/v1/unregister",
                json=payload,
                timeout=self.config.get('timeout_seconds', 10)
            )
            
            if response.status_code == 200:
                print("✅ Desregistro exitoso")
                return True
            else:
                print(f"⚠️  Error en desregistro: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error desregistrando: {e}")
            return False
    
    def run(self) -> int:
        """Ejecutar el agente"""
        try:
            print("🎓 EduMon Agent - Versión Simple")
            print("=" * 40)
            
            # Solicitar consentimiento
            if not self.get_consent():
                print("❌ Consentimiento no otorgado")
                return 0
            
            # Registrarse con el servidor
            if not self.register_with_server():
                print("❌ No se pudo conectar con el servidor")
                return 1
            
            # Mostrar información
            print("\\n🚀 AGENTE INICIADO")
            print("=" * 40)
            print(f"🆔 Device ID: {self.device_id}")
            print(f"🔗 Servidor: {self.config['server_url']}")
            print(f"🏫 Aula: {self.config.get('classroom_id', 'No configurada')}")
            print(f"⏱️  Intervalo: {self.config.get('heartbeat_seconds', 15)} segundos")
            print("\\n⚠️  Presiona Ctrl+C para detener")
            print("=" * 40)
            print()
            
            # Loop principal
            self.running = True
            heartbeat_interval = self.config.get('heartbeat_seconds', 15)
            
            while self.running:
                try:
                    # Enviar heartbeat
                    if not self.send_heartbeat():
                        print("⚠️  Fallo en heartbeat, continuando...")
                    
                    # Esperar
                    time.sleep(heartbeat_interval)
                    
                except KeyboardInterrupt:
                    break
            
            # Desregistrarse
            self.unregister_from_server("user_interrupt")
            
            print("\\n🛑 Agente detenido correctamente")
            return 0
            
        except Exception as e:
            print(f"❌ Error ejecutando agente: {e}")
            return 1
        finally:
            self.running = False

def main():
    """Función principal"""
    agent = SimpleAgent()
    return agent.run()

if __name__ == "__main__":
    sys.exit(main())