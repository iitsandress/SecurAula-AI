import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, Any
import time

from fastapi import FastAPI, Request, HTTPException, Header, Depends, Query
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
        pass
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key

# Función para verificar API key opcional (para dashboard)
def verify_api_key_optional(api_key: Optional[str] = Query(None)) -> bool:
    """Verificar API key opcional para dashboard"""
    if not api_key:
        return False
    return api_key == API_KEY

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
app = FastAPI(
    title="EduMon API", 
    version="2.0.0", 
    description="Servidor educativo de monitoreo con consentimiento y auditoría"
)

@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "version": "2.0.0", "api_key_configured": bool(API_KEY)}

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

# Dashboard público (sin requerir API key en la URL)
@app.get("/dashboard")
async def dashboard(api_key: Optional[str] = Query(None)):
    from fastapi.responses import HTMLResponse
    
    # Verificar si se proporcionó API key
    has_api_key = verify_api_key_optional(api_key)
    
    if not has_api_key:
        # Mostrar página de login para API key
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>EduMon - Acceso al Dashboard</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .login-container {{ 
                    background: rgba(255,255,255,0.95); 
                    padding: 40px; 
                    border-radius: 20px; 
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1); 
                    text-align: center;
                    max-width: 400px;
                    width: 90%;
                    backdrop-filter: blur(10px);
                }}
                .logo {{ font-size: 3em; margin-bottom: 20px; }}
                h1 {{ color: #333; margin-bottom: 10px; font-size: 1.8em; }}
                p {{ color: #666; margin-bottom: 30px; line-height: 1.5; }}
                .form-group {{ margin-bottom: 20px; text-align: left; }}
                label {{ display: block; margin-bottom: 5px; color: #333; font-weight: 500; }}
                input {{ 
                    width: 100%; 
                    padding: 12px; 
                    border: 2px solid #e0e0e0; 
                    border-radius: 8px; 
                    font-size: 16px;
                    transition: border-color 0.3s;
                }}
                input:focus {{ 
                    outline: none; 
                    border-color: #667eea; 
                    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                }}
                button {{ 
                    width: 100%; 
                    padding: 12px; 
                    background: linear-gradient(135deg, #667eea, #764ba2); 
                    color: white; 
                    border: none; 
                    border-radius: 8px; 
                    font-size: 16px; 
                    font-weight: 500;
                    cursor: pointer;
                    transition: transform 0.2s;
                }}
                button:hover {{ transform: translateY(-2px); }}
                .hint {{ 
                    background: #e3f2fd; 
                    color: #1976d2; 
                    padding: 15px; 
                    border-radius: 8px; 
                    margin-top: 20px;
                    font-size: 0.9em;
                }}
                .api-key-display {{ 
                    background: #f5f5f5; 
                    padding: 10px; 
                    border-radius: 5px; 
                    font-family: monospace; 
                    margin: 10px 0;
                    border: 1px solid #ddd;
                }}
            </style>
        </head>
        <body>
            <div class="login-container">
                <div class="logo">🎓</div>
                <h1>EduMon Dashboard</h1>
                <p>Ingresa la clave API para acceder al panel de control del profesor</p>
                
                <form id="loginForm">
                    <div class="form-group">
                        <label for="apiKey">Clave API:</label>
                        <input type="password" id="apiKey" name="apiKey" placeholder="Ingresa tu clave API" required>
                    </div>
                    <button type="submit">🚀 Acceder al Dashboard</button>
                </form>
                
                <div class="hint">
                    <strong>💡 Clave API por defecto:</strong>
                    <div class="api-key-display">{API_KEY}</div>
                    <small>Esta es la clave configurada en el servidor</small>
                </div>
            </div>
            
            <script>
                document.getElementById('loginForm').addEventListener('submit', function(e) {{
                    e.preventDefault();
                    const apiKey = document.getElementById('apiKey').value;
                    if (apiKey) {{
                        window.location.href = '/dashboard?api_key=' + encodeURIComponent(apiKey);
                    }}
                }});
                
                // Auto-rellenar con la clave por defecto
                document.getElementById('apiKey').value = '{API_KEY}';
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html)
    
    # Si tiene API key válida, mostrar dashboard
    clients = load_clients()
    now = datetime.now(timezone.utc)
    
    # Generar tabla de clientes
    rows = []
    total = online = offline = 0
    
    for device_id, client in clients.items():
        total += 1
        metrics = client.get("metrics", {})
        cpu = metrics.get("cpu_percent", 0)
        mem = metrics.get("mem_percent", 0)
        uptime = metrics.get("uptime_seconds", 0)
        
        # Calcular estado
        last_seen = client.get("last_seen", "")
        try:
            last_dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
            seconds_ago = (now - last_dt).total_seconds()
            if seconds_ago <= 60:
                status = "🟢 En línea"
                status_class = "online"
                online += 1
            else:
                status = "🔴 Desconectado"
                status_class = "offline"
                offline += 1
        except:
            status = "⚪ Desconocido"
            status_class = "unknown"
            offline += 1
        
        # Formatear uptime
        hours, remainder = divmod(uptime, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        rows.append(f"""
        <tr class="{status_class}">
            <td style="font-family: monospace; font-size: 0.9em;">{device_id}</td>
            <td><strong>{client.get('hostname', '')}</strong></td>
            <td>{client.get('username', '')}</td>
            <td><span class="classroom-tag">{client.get('classroom_id', 'Sin aula')}</span></td>
            <td><div class="metric-bar"><div class="metric-fill" style="width: {cpu}%"></div><span>{cpu}%</span></div></td>
            <td><div class="metric-bar"><div class="metric-fill" style="width: {mem}%"></div><span>{mem}%</span></div></td>
            <td>{uptime_str}</td>
            <td><span class="status-badge {status_class}">{status}</span></td>
            <td style="font-size: 0.8em;">{last_seen.split('T')[1][:8] if 'T' in last_seen else last_seen}</td>
        </tr>
        """)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv="refresh" content="10">
        <title>EduMon - Dashboard del Profesor</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .header {{ 
                background: rgba(255,255,255,0.1); 
                backdrop-filter: blur(10px);
                color: white; 
                padding: 20px; 
                text-align: center; 
                border-bottom: 1px solid rgba(255,255,255,0.2);
            }}
            .header h1 {{ font-size: 2.5em; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }}
            .header p {{ opacity: 0.9; font-size: 1.1em; }}
            .container {{ max-width: 1400px; margin: 20px auto; padding: 0 20px; }}
            .stats {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 20px; 
                margin: 20px 0; 
            }}
            .stat-card {{ 
                background: rgba(255,255,255,0.95); 
                padding: 25px; 
                border-radius: 15px; 
                box-shadow: 0 8px 32px rgba(0,0,0,0.1); 
                text-align: center;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }}
            .stat-number {{ font-size: 3em; font-weight: bold; color: #667eea; margin-bottom: 5px; }}
            .stat-label {{ color: #666; font-size: 1.1em; }}
            .table-container {{ 
                background: rgba(255,255,255,0.95); 
                border-radius: 15px; 
                overflow: hidden; 
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ 
                background: linear-gradient(135deg, #667eea, #764ba2); 
                color: white; 
                padding: 15px 12px; 
                text-align: left; 
                font-weight: 600;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            td {{ padding: 12px; border-bottom: 1px solid #f0f0f0; }}
            tr:hover {{ background: rgba(102, 126, 234, 0.05); }}
            .online {{ background: rgba(76, 175, 80, 0.05); }}
            .offline {{ background: rgba(244, 67, 54, 0.05); }}
            .status-badge {{ 
                padding: 4px 8px; 
                border-radius: 12px; 
                font-size: 0.8em; 
                font-weight: 500;
            }}
            .status-badge.online {{ background: rgba(76, 175, 80, 0.1); color: #4CAF50; }}
            .status-badge.offline {{ background: rgba(244, 67, 54, 0.1); color: #f44336; }}
            .status-badge.unknown {{ background: rgba(158, 158, 158, 0.1); color: #9e9e9e; }}
            .classroom-tag {{ 
                background: #e3f2fd; 
                color: #1976d2; 
                padding: 2px 8px; 
                border-radius: 8px; 
                font-size: 0.8em;
                font-weight: 500;
            }}
            .metric-bar {{ 
                position: relative; 
                background: #f0f0f0; 
                border-radius: 8px; 
                height: 20px; 
                overflow: hidden;
                min-width: 60px;
            }}
            .metric-fill {{ 
                background: linear-gradient(90deg, #4CAF50, #8BC34A); 
                height: 100%; 
                transition: width 0.3s ease;
            }}
            .metric-bar span {{ 
                position: absolute; 
                top: 50%; 
                left: 50%; 
                transform: translate(-50%, -50%); 
                font-size: 0.7em; 
                font-weight: bold; 
                color: #333;
                text-shadow: 0 1px 2px rgba(255,255,255,0.8);
            }}
            .links {{ 
                margin: 30px 0; 
                text-align: center; 
                display: flex; 
                justify-content: center; 
                gap: 15px; 
                flex-wrap: wrap;
            }}
            .links a {{ 
                display: inline-block; 
                padding: 12px 24px; 
                background: rgba(255,255,255,0.9); 
                color: #667eea; 
                text-decoration: none; 
                border-radius: 25px; 
                font-weight: 500;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            .links a:hover {{ 
                background: white; 
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.15);
            }}
            .footer {{ 
                text-align: center; 
                margin: 30px 0; 
                color: rgba(255,255,255,0.8); 
                font-size: 0.9em;
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }}
            .no-clients {{ 
                text-align: center; 
                padding: 40px; 
                color: #666; 
                font-size: 1.1em;
            }}
            .refresh-info {{ 
                background: rgba(255,255,255,0.1); 
                color: white; 
                padding: 10px 20px; 
                border-radius: 25px; 
                display: inline-block; 
                margin: 10px 0;
                font-size: 0.9em;
            }}
            .logout-btn {{
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(255,255,255,0.2);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 0.9em;
            }}
            .logout-btn:hover {{
                background: rgba(255,255,255,0.3);
            }}
            @media (max-width: 768px) {{
                .container {{ padding: 0 10px; }}
                .stats {{ grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }}
                .stat-card {{ padding: 15px; }}
                .stat-number {{ font-size: 2em; }}
                table {{ font-size: 0.8em; }}
                th, td {{ padding: 8px 6px; }}
                .logout-btn {{ position: static; margin: 10px; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <button class="logout-btn" onclick="window.location.href='/dashboard'">🚪 Cerrar Sesión</button>
            <h1>🎓 EduMon Dashboard</h1>
            <p>Sistema de Monitoreo Educativo con Consentimiento</p>
            <div class="refresh-info">🔄 Actualización automática cada 10 segundos</div>
        </div>
        
        <div class="container">
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{total}</div>
                    <div class="stat-label">📊 Total Equipos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{online}</div>
                    <div class="stat-label">🟢 En Línea</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{offline}</div>
                    <div class="stat-label">🔴 Desconectados</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{round((online/total*100) if total > 0 else 0)}%</div>
                    <div class="stat-label">📈 Conectividad</div>
                </div>
            </div>
            
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>🆔 Device ID</th>
                            <th>💻 Hostname</th>
                            <th>👤 Usuario</th>
                            <th>🏫 Aula</th>
                            <th>🔥 CPU</th>
                            <th>🧠 RAM</th>
                            <th>⏱️ Uptime</th>
                            <th>📡 Estado</th>
                            <th>🕐 Última Conexión</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows) if rows else '<tr><td colspan="9" class="no-clients">📭 No hay clientes conectados<br><small>Los estudiantes deben ejecutar el agente EduMon</small></td></tr>'}
                    </tbody>
                </table>
            </div>
            
            <div class="links">
                <a href="/docs">📖 Documentación API</a>
                <a href="/health">❤️ Estado del Servidor</a>
                <a href="/api/v1/clients?api_key={api_key}">📊 API Clientes (JSON)</a>
            </div>
            
            <div class="footer">
                <p><strong>🔑 API Key:</strong> {api_key} | <strong>🕐 Hora:</strong> {now.strftime('%H:%M:%S')}</p>
                <p>EduMon v2.0 - Sistema educativo de monitoreo ético | Desarrollado con ❤️ para la educación</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)

# Función principal para ejecutar el servidor
def run_server():
    import uvicorn
    print("🎓 Iniciando EduMon Server - Programa del Profesor")
    print(f"🔑 API Key: {API_KEY}")
    print("📊 Dashboard: http://190.84.119.196:8000/dashboard")
    print("🔧 API Docs: http://190.84.119.196:8000/docs")
    print("❤️ Health: http://190.84.119.196:8000/health")
    print("\n💡 IMPORTANTE: El dashboard ahora tiene una página de login")
    print(f"   Usa la clave API: {API_KEY}")
    print("\n⚠️  Presiona Ctrl+C para detener el servidor")
    print("=" * 60)
    
    try:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_server()