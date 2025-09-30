import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Default API Key. In a real production environment, this should be loaded
    # from an environment variable or a secret management system.
    EDUMON_API_KEY: str = "S1R4X"
    
    # Data storage configuration
    # Apunta al directorio backend para datos y logs
    BACKEND_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    BASE_DIR: str = os.path.dirname(BACKEND_DIR)  # Directorio raíz del proyecto
    DATA_DIR: str = os.path.join(BACKEND_DIR, "data")
    LOG_DIR: str = os.path.join(BACKEND_DIR, "logs")
    CLIENTS_FILE: str = os.path.join(DATA_DIR, "clients.json")
    AUDIT_LOG_FILE: str = os.path.join(LOG_DIR, "audit.log")

    class Config:
        case_sensitive = True

settings = Settings()
