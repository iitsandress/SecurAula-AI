import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, Any
import time

from fastapi import FastAPI, Request, HTTPException, Header, Depends
from pydantic import BaseModel, Field

# --- Configuración ---
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.environ.get("EDUMON_DATA_DIR", os.path.join(BASE_DIR, "data"))
LOG_DIR = os.path.join(BASE_DIR, "logs")
API_KEY = os.environ.get("EDUMON_API_KEY", "S1R4X")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
CLIENTS_FILE = os.path.join(DATA_DIR, "clients.json")
AUDIT_LOG = os.path.join(LOG_DIR, "audit.log")

# --- Utilidades ---
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def audit_log(action: str, actor: str, request: Optional[Request] = None, details: Optional[Dict[str, Any]] = None) -> None:
    entry = {
        "ts": now_iso(),
        "action": action,
        "actor": actor,
        "ip": getattr(request.client, "host", None) if request else None,
        "details": details or {},
    }
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_clients() -> Dict[str, Any]:
    if not os.path.exists(CLIENTS_FILE):
        return {}
    try:
        with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_clients(clients: Dict[str, Any]) -> None:
    tmp_path = CLIENTS_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(clients, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, CLIENTS_FILE)


# --- Seguridad (API Key) ---
async def require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> str:
    if not API_KEY or API_KEY == "changeme":
        # Entorno de desarrollo; por favor configure EDUMON_API_KEY antes de usar en producción
        pass
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key


# --- Modelos ---
class RegisterRequest(BaseModel):
    device_id: str = Field(..., min_length=4, max_length=200)
    hostname: str = Field(..., min_length=1, max_length=200)
    username: str = Field(..., min_length=1, max_length=200)
    consent: bool
    classroom_id: Optional[str] = Field(default=None, max_length=100)


class RegisterResponse(BaseModel):
    session_id: str


class Metrics(BaseModel):
    cpu_percent: float = Field(..., ge=0, le=100)
    mem_percent: float = Field(..., ge=0, le=100)
    uptime_seconds: int = Field(..., ge=0)


class HeartbeatRequest(BaseModel):
    device_id: str
    session_id: str
    metrics: Metrics


class UnregisterRequest(BaseModel):
    device_id: str
    session_id: str
    reason: Optional[str] = None


# --- Aplicación ---
app = FastAPI(title="EduMon API", version="0.1.0", description="Servidor educativo de monitoreo con consentimiento y auditoría")

# Incluir dashboard y control si están disponibles
try:
    import dashboard
    app.include_router(dashboard.router)
except Exception:
    print("Dashboard module not available")

try:
    import control
    app.include_router(control.router)
except Exception:
    print("Control module not available")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/register", response_model=RegisterResponse)
async def register(payload: RegisterRequest, request: Request, _: str = Depends(require_api_key)) -> RegisterResponse:
    if not payload.consent:
        raise HTTPException(status_code=400, detail="Consent is required")

    clients = load_clients()
    session_id = str(uuid.uuid4())

    clients[payload.device_id] = {
        "session_id": session_id,
        "hostname": payload.hostname,
        "username": payload.username,
        "classroom_id": payload.classroom_id,
        "consent": True,
        "last_seen": now_iso(),
        "session_started": now_iso(),
        "metrics": None,
    }
    save_clients(clients)

    audit_log("register", actor=payload.device_id, request=request, details={
        "hostname": payload.hostname,
        "username": payload.username,
        "classroom_id": payload.classroom_id,
    })

    return RegisterResponse(session_id=session_id)


@app.post("/api/v1/heartbeat")
async def heartbeat(payload: HeartbeatRequest, request: Request, _: str = Depends(require_api_key)) -> Dict[str, str]:
    clients = load_clients()
    client = clients.get(payload.device_id)

    if not client or client.get("session_id") != payload.session_id:
        raise HTTPException(status_code=401, detail="Unknown device or invalid session")

    client["metrics"] = payload.metrics.model_dump()
    client["last_seen"] = now_iso()
    save_clients(clients)

    audit_log("heartbeat", actor=payload.device_id, request=request, details={
        "cpu_percent": payload.metrics.cpu_percent,
        "mem_percent": payload.metrics.mem_percent,
        "uptime_seconds": payload.metrics.uptime_seconds,
    })

    return {"status": "ok"}


@app.post("/api/v1/unregister")
async def unregister(payload: UnregisterRequest, request: Request, _: str = Depends(require_api_key)) -> Dict[str, str]:
    clients = load_clients()
    client = clients.get(payload.device_id)

    if not client or client.get("session_id") != payload.session_id:
        # Idempotente: responder ok aunque no coincida, pero registrar
        audit_log("unregister_mismatch", actor=payload.device_id, request=request, details={
            "reason": payload.reason,
        })
        return {"status": "ok"}

    client["consent"] = False
    client["session_ended"] = now_iso()
    save_clients(clients)

    audit_log("unregister", actor=payload.device_id, request=request, details={
        "reason": payload.reason,
    })

    return {"status": "ok"}


@app.get("/api/v1/clients")
async def list_clients(_: str = Depends(require_api_key)) -> Dict[str, Any]:
    clients = load_clients()
    return {"clients": clients}


# Dashboard básico integrado
@app.get("/dashboard")
async def dashboard(_: str = Depends(require_api_key)):
    from fastapi.responses import HTMLResponse
    
    clients = load_clients()
    
    # Generar tabla de clientes
    rows = []
    for device_id, client in clients.items():
        metrics = client.get("metrics", {})
        cpu = metrics.get("cpu_percent", 0)
        mem = metrics.get("mem_percent", 0)
        
        rows.append(f"""
        <tr>
            <td>{device_id}</td>
            <td>{client.get('hostname', '')}</td>
            <td>{client.get('username', '')}</td>
            <td>{client.get('classroom_id', '')}</td>
            <td>{cpu}%</td>
            <td>{mem}%</td>
            <td>{client.get('last_seen', '')}</td>
        </tr>
        """)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>EduMon Dashboard</title>
        <meta charset="utf-8">
        <meta http-equiv="refresh" content="15">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .header {{ background: #4CAF50; color: white; padding: 10px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎓 EduMon - Dashboard del Profesor</h1>
            <p>Monitoreo educativo con consentimiento | Actualización automática cada 15 segundos</p>
        </div>
        
        <h2>Clientes Conectados ({len(clients)})</h2>
        
        <table>
            <thead>
                <tr>
                    <th>Device ID</th>
                    <th>Hostname</th>
                    <th>Usuario</th>
                    <th>Aula</th>
                    <th>CPU</th>
                    <th>RAM</th>
                    <th>Última Conexión</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        
        <div style="margin-top: 20px; padding: 10px; background: #f9f9f9;">
            <h3>Enlaces Útiles:</h3>
            <ul>
                <li><a href="/docs">📖 Documentación de la API</a></li>
                <li><a href="/health">❤️ Estado del Servidor</a></li>
                <li><a href="/api/v1/clients">📊 API de Clientes (JSON)</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)


if __name__ == "__main__":
    import uvicorn
    print("🎓 Iniciando EduMon Server - Programa del Profesor")
    print(f"🔑 API Key: {API_KEY}")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("🔧 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)