import os
import uuid
import socket
import getpass
import time
import threading
from typing import Dict, Any, Optional

from .core.metrics import get_system_metrics
from .core.api_client import ApiClient

class EduMonAgent:
    def __init__(self):
        self.device_id = self._get_or_create_device_id()
        self.session_id: Optional[str] = None
        self.running = False
        self.api_client: Optional[ApiClient] = None
        self.agent_thread: Optional[threading.Thread] = None
        self.config: Dict[str, Any] = {}
        self.on_status_update = lambda status: None
        self.on_metrics_update = lambda metrics: None

    def _get_or_create_device_id(self) -> str:
        device_file = "device_id.txt"
        if os.path.exists(device_file):
            try:
                with open(device_file, 'r') as f:
                    return f.read().strip()
            except IOError:
                pass
        device_id = str(uuid.uuid4())
        try:
            with open(device_file, 'w') as f:
                f.write(device_id)
        except IOError:
            pass
        return device_id

    def _agent_loop(self):
        while self.running:
            if not self.api_client or not self.session_id:
                break

            metrics = get_system_metrics()
            self.on_metrics_update(metrics)

            payload = {
                "device_id": self.device_id,
                "session_id": self.session_id,
                "metrics": metrics
            }

            if not self.api_client.send_heartbeat(payload):
                self.on_status_update("⚠️ Error enviando datos")
            else:
                self.on_status_update("🟢 Conectado")

            for _ in range(150): # 15s in 0.1s intervals
                if not self.running:
                    break
                time.sleep(0.1)

    def start(self, config: Dict[str, Any]) -> bool:
        if self.running:
            return True
        
        self.config = config
        self.api_client = ApiClient(config['server_url'], config['api_key'])

        register_payload = {
            "device_id": self.device_id,
            "hostname": socket.gethostname(),
            "username": getpass.getuser(),
            "consent": True,
            "classroom_id": self.config.get('classroom_id')
        }

        self.on_status_update("🟡 Registrando...")
        self.session_id = self.api_client.register(register_payload)

        if not self.session_id:
            self.on_status_update("🔴 Error de registro")
            return False

        self.running = True
        self.agent_thread = threading.Thread(target=self._agent_loop, daemon=True)
        self.agent_thread.start()
        self.on_status_update("🟢 Conectado y enviando datos")
        return True

    def stop(self, reason: str = "user_request"):
        if not self.running or not self.api_client or not self.session_id:
            return

        self.running = False
        self.on_status_update("⚪ Desconectando...")
        
        unregister_payload = {
            "device_id": self.device_id,
            "session_id": self.session_id,
            "reason": reason
        }
        self.api_client.unregister(unregister_payload)
        
        if self.agent_thread:
            self.agent_thread.join(timeout=2)

        self.on_status_update("🛑 Desconectado")
