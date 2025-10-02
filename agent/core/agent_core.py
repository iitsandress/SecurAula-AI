import time
import threading
import logging
import socket
import getpass
from typing import Optional
import mss
import base64

from .config import AgentConfig
from .metrics import MetricsCollector
from .logging_config import AuditLogger
from .api_client import ApiClient


class AgentCore:
    """Core agent functionality"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.metrics_collector = MetricsCollector()
        self.audit_logger = AuditLogger()
        self.logger = logging.getLogger(__name__)
        self.api_client = ApiClient(config)

        # Session state
        self.session_id: Optional[str] = None
        self.device_id: str = self.metrics_collector.get_device_id()
        self.is_running = False
        self.stop_event = threading.Event()
        self.screenshot_requested = threading.Event()

    def capture_screenshot(self) -> Optional[str]:
        """Captures a screenshot, encodes it in base64 and returns it."""
        try:
            with mss.mss() as sct:
                sct_img = sct.grab(sct.monitors[1])
                img_bytes = mss.tools.to_png(sct_img.rgb, sct_img.size)
                return base64.b64encode(img_bytes).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error capturing screenshot: {e}")
            return None

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
        print("• Capturas de pantalla (bajo demanda)")
        print("\nNUNCA se capturan:")
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
        system_info = self.metrics_collector.get_system_info()

        payload = {
            "device_id": self.device_id,
            "hostname": socket.gethostname(),
            "username": getpass.getuser(),
            "consent": True,
            "classroom_id": self.config.classroom_id,
            "os_info": system_info.get("platform", "Unknown")
        }

        self.logger.info(f"Registering with server: {self.config.server_url}")
        session_id = self.api_client.register(payload)

        if session_id:
            self.session_id = session_id
            self.logger.info(f"Registration successful. Session ID: {self.session_id}")
            self.audit_logger.log_event("registration_success", {
                "session_id": self.session_id,
                "server_url": self.config.server_url,
                "classroom_id": self.config.classroom_id
            })
            return True
        else:
            self.logger.error(f"Registration failed")
            return False

    def send_heartbeat(self) -> bool:
        """Send heartbeat with metrics to server"""
        if not self.session_id:
            self.logger.error("No active session for heartbeat")
            return False

        metrics = self.metrics_collector.collect_all_metrics(self.config)

        payload = {
            "device_id": self.device_id,
            "session_id": self.session_id,
            "metrics": metrics
        }

        if self.api_client.send_heartbeat(payload):
            self.logger.debug("Heartbeat sent successfully")
            return True
        else:
            self.logger.warning("Heartbeat failed, continuing...")
            return False

    def unregister_from_server(self, reason: str = "user_request") -> bool:
        """Unregister from server"""
        if not self.session_id:
            return True  # Already unregistered

        payload = {
            "device_id": self.device_id,
            "session_id": self.session_id,
            "reason": reason
        }

        if self.api_client.unregister(payload):
            self.logger.info("Unregistered successfully")
            self.audit_logger.log_event("unregistration_success", {
                "session_id": self.session_id,
                "reason": reason
            })
            self.session_id = None
            return True
        else:
            self.logger.warning(f"Unregistration failed")
            return False

    def heartbeat_loop(self):
        """Main heartbeat loop"""
        self.logger.info("Starting heartbeat loop")

        while not self.stop_event.is_set():
            try:
                if not self.send_heartbeat():
                    self.logger.warning("Heartbeat failed, continuing...")

                # Check for screenshot request
                response = self.api_client.session.post(f"{self.config.server_url}/api/v1/clients/{self.device_id}/screenshot_request")
                if response.status_code == 200:
                    self.screenshot_requested.set()

                if self.stop_event.wait(self.config.heartbeat_seconds):
                    break

            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {e}")
                time.sleep(5)

        self.logger.info("Heartbeat loop stopped")

    def start(self) -> bool:
        """Start the agent"""
        if self.is_running:
            self.logger.warning("Agent is already running")
            return False

        if not self.get_consent():
            self.logger.info("Consent not granted")
            return False

        if not self.register_with_server():
            self.logger.error("Failed to register with server")
            return False

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

        self.is_running = False
        self.stop_event.set()

        if hasattr(self, 'heartbeat_thread') and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5)

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