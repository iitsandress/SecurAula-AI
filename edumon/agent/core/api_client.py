import requests
from typing import Dict, Any, Optional

from .config import AgentConfig


class ApiClient:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.config.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'EduMon-Agent/3.0.0'
        })
        self.session.verify = self.config.verify_ssl

    def register(self, payload: Dict[str, Any]) -> Optional[str]:
        """Registra el agente y devuelve el session_id."""
        try:
            response = self.session.post(
                f"{self.config.server_url}/api/v1/register",
                json=payload,
                timeout=self.config.timeout_seconds
            )
            if response.status_code == 200:
                return response.json().get("session_id")
            print(f"Error en el registro: {response.status_code} - {response.text}")
            return None
        except requests.RequestException as e:
            print(f"Error de conexión al registrar: {e}")
            return None

    def send_heartbeat(self, payload: Dict[str, Any]) -> bool:
        """Envía un heartbeat con métricas."""
        try:
            response = self.session.post(
                f"{self.config.server_url}/api/v1/heartbeat",
                json=payload,
                timeout=self.config.timeout_seconds
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def unregister(self, payload: Dict[str, Any]) -> bool:
        """Desregistra el agente del servidor."""
        try:
            response = self.session.post(
                f"{self.config.server_url}/api/v1/unregister",
                json=payload,
                timeout=self.config.timeout_seconds
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
