"""
Core agent functionality for headless operation
"""
import time
import threading
import logging
import requests
import uuid
import socket
import getpass
from typing import Optional, Dict, Any
from datetime import datetime

from .config import AgentConfig
from .metrics import MetricsCollector
from .logging_config import AuditLogger


class AgentCore:
    """Core agent functionality"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.metrics_collector = MetricsCollector()
        self.audit_logger = AuditLogger()
        self.logger = logging.getLogger(__name__)
        
        # Session state
        self.session_id: Optional[str] = None
        self.device_id: str = self.metrics_collector.get_device_id()
        self.is_running = False
        self.stop_event = threading.Event()
        
        # HTTP session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.config.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'EduMon-Agent/2.0.0'
        })
        
        if not self.config.verify_ssl:
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def get_consent(self) -> bool:
        """Get user consent (headless version)"""
        print("\n" + "="*60)
        print("EDUMON - CONSENTIMIENTO PARA MONITOREO EDUCATIVO")
        print("="*60)
        print("\nEste agente enviará ÚNICAMENTE los siguientes datos:")
        print("• Identificador del equipo (anónimo)")
        print("• Nombre del host y usuario del sistema")
        print("• Métricas de rendimiento: CPU, RAM, disco, red")
        print("• Tiempo de actividad del sistema")
        print("• Información de procesos (solo nombres)")
        print("\nNUNCA se capturan:")
        print("• Capturas de pantalla")
        print("• Pulsaciones de teclado")
        print("• Contenido de archivos")
        print("• Historial de navegación")
        print("• Datos personales")
        print("\nPuede detener el monitoreo en cualquier momento con Ctrl+C")
        print("="*60)
        
        while True:
            response = input("\n¿Acepta participar en esta sesión de monitoreo? (si/no): ").strip().lower()
            if response in ['si', 'sí', 's', 'yes', 'y']:
                self.audit_logger.log_event("consent_granted", {"device_id": self.device_id})
                return True
            elif response in ['no', 'n']:
                self.audit_logger.log_event("consent_denied", {"device_id": self.device_id})
                return False
            else:
                print("Por favor responda 'si' o 'no'")
    
    def register_with_server(self) -> bool:
        """Register with the server"""
        try:
            system_info = self.metrics_collector.get_system_info()
            
            payload = {
                "device_id": self.device_id,
                "hostname": socket.gethostname(),
                "username": getpass.getuser(),
                "consent": True,
                "classroom_id": self.config.classroom_id,
                "ip_address": None,  # Server will detect this
                "os_info": system_info.get("platform", "Unknown")
            }
            
            self.logger.info(f"Registering with server: {self.config.server_url}")
            
            response = self.session.post(
                f"{self.config.server_url}/api/v1/clients/register",
                json=payload,
                timeout=self.config.timeout_seconds
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data["session_id"]
                self.logger.info(f"Registration successful. Session ID: {self.session_id}")
                
                self.audit_logger.log_event("registration_success", {
                    "session_id": self.session_id,
                    "server_url": self.config.server_url,
                    "classroom_id": self.config.classroom_id
                })
                
                return True
            else:
                self.logger.error(f"Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat with metrics to server"""
        try:
            if not self.session_id:
                self.logger.error("No active session for heartbeat")
                return False
            
            # Collect metrics
            metrics = self.metrics_collector.collect_all_metrics(self.config)
            
            payload = {
                "device_id": self.device_id,
                "session_id": self.session_id,
                "metrics": metrics
            }
            
            response = self.session.post(
                f"{self.config.server_url}/api/v1/clients/heartbeat",
                json=payload,
                timeout=self.config.timeout_seconds
            )
            
            if response.status_code == 200:
                self.logger.debug("Heartbeat sent successfully")
                return True
            else:
                self.logger.warning(f"Heartbeat failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Heartbeat error: {e}")
            return False
    
    def check_server_control(self) -> bool:
        """Check if server wants to stop this agent"""
        try:
            response = self.session.get(
                f"{self.config.server_url}/api/v1/control",
                timeout=self.config.timeout_seconds
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check global stop
                if data.get("stop_all", False):
                    self.logger.info("Server requested global stop")
                    return True
                
                # Check device-specific stop
                stop_list = data.get("stop_list", [])
                if self.device_id in stop_list:
                    self.logger.info("Server requested stop for this device")
                    return True
                
                return False
            else:
                self.logger.warning(f"Control check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Control check error: {e}")
            return False
    
    def unregister_from_server(self, reason: str = "user_request") -> bool:
        """Unregister from server"""
        try:
            if not self.session_id:
                return True  # Already unregistered
            
            payload = {
                "device_id": self.device_id,
                "session_id": self.session_id,
                "reason": reason
            }
            
            response = self.session.post(
                f"{self.config.server_url}/api/v1/clients/unregister",
                json=payload,
                timeout=self.config.timeout_seconds
            )
            
            if response.status_code == 200:
                self.logger.info("Unregistered successfully")
                self.audit_logger.log_event("unregistration_success", {
                    "session_id": self.session_id,
                    "reason": reason
                })
                self.session_id = None
                return True
            else:
                self.logger.warning(f"Unregistration failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Unregistration error: {e}")
            return False
    
    def heartbeat_loop(self):
        """Main heartbeat loop"""
        self.logger.info("Starting heartbeat loop")
        
        while not self.stop_event.is_set():
            try:
                # Check server control
                if self.check_server_control():
                    self.logger.info("Server requested stop")
                    self.stop()
                    break
                
                # Send heartbeat
                if not self.send_heartbeat():
                    self.logger.warning("Heartbeat failed, continuing...")
                
                # Wait for next heartbeat
                if self.stop_event.wait(self.config.heartbeat_seconds):
                    break  # Stop event was set
                    
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {e}")
                time.sleep(5)  # Brief pause before retrying
        
        self.logger.info("Heartbeat loop stopped")
    
    def start(self) -> bool:
        """Start the agent"""
        if self.is_running:
            self.logger.warning("Agent is already running")
            return False
        
        # Get consent
        if not self.get_consent():
            self.logger.info("Consent not granted")
            return False
        
        # Register with server
        if not self.register_with_server():
            self.logger.error("Failed to register with server")
            return False
        
        # Start heartbeat loop in background thread
        self.is_running = True
        self.stop_event.clear()
        
        self.heartbeat_thread = threading.Thread(
            target=self.heartbeat_loop,
            name="HeartbeatThread",
            daemon=True
        )
        self.heartbeat_thread.start()
        
        self.logger.info("Agent started successfully")
        return True
    
    def stop(self, reason: str = "user_request"):
        """Stop the agent"""
        if not self.is_running:
            return
        
        self.logger.info(f"Stopping agent. Reason: {reason}")
        
        # Signal stop
        self.is_running = False
        self.stop_event.set()
        
        # Wait for heartbeat thread to finish
        if hasattr(self, 'heartbeat_thread') and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5)
        
        # Unregister from server
        self.unregister_from_server(reason)
        
        self.logger.info("Agent stopped")
    
    def run(self) -> int:
        """Run the agent (blocking)"""
        try:
            if not self.start():
                return 1
            
            print(f"\nEduMon Agent running...")
            print(f"Device ID: {self.device_id}")
            print(f"Session ID: {self.session_id}")
            print(f"Server: {self.config.server_url}")
            print(f"Classroom: {self.config.classroom_id or 'Not set'}")
            print("\nPress Ctrl+C to stop")
            
            # Wait for stop signal
            try:
                while self.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nReceived stop signal...")
                self.stop("user_interrupt")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error running agent: {e}")
            return 1
        finally:
            # Cleanup
            self.session.close()