import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, Any, List

from fastapi import FastAPI, Request, HTTPException, Header, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .core.config import settings
from .core.database import create_tables
from .models import schemas
from .models import *  # Import all models for SQLAlchemy
from .services import storage

# Try to import database service, fallback if not available
try:
    from .services.database_service import db_service
    USE_DB_SERVICE = True
except ImportError:
    USE_DB_SERVICE = False
    print("Warning: database_service not available, using JSON storage only")

# --- App Initialization ---
app = FastAPI(
    title="EduMon Server",
    version="4.0.0",
    description="Servidor educativo de monitoreo - Versión 'Infinita'"
)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        create_tables()
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")

import os
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# --- Security ---
async def require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> str:
    if not x_api_key or x_api_key != settings.EDUMON_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key

def verify_api_key_optional(api_key: Optional[str] = Query(None)) -> bool:
    return api_key == settings.EDUMON_API_KEY

# --- API Endpoints ---
@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "version": app.version,
        "api_key_configured": bool(settings.EDUMON_API_KEY),
        "database_service": USE_DB_SERVICE
    }

@app.post("/api/v1/register", response_model=schemas.RegisterResponse)
async def register(payload: schemas.RegisterRequest, request: Request, _: str = Depends(require_api_key)) -> schemas.RegisterResponse:
    if not payload.consent:
        raise HTTPException(status_code=400, detail="Consent is required")

    if USE_DB_SERVICE:
        session_id = await db_service.register_client(
            device_id=payload.device_id,
            hostname=payload.hostname,
            username=payload.username,
            classroom_id=payload.classroom_id,
            ip_address=request.client.host if request.client else None
        )

        await db_service.audit_log("register", actor=payload.device_id, ip=request.client.host if request.client else None, details={
            "hostname": payload.hostname,
            "username": payload.username,
            "classroom_id": payload.classroom_id,
        })
    else:
        # Fallback to JSON storage
        clients = await storage.load_clients()
        session_id = str(uuid.uuid4())

        clients[payload.device_id] = {
            "session_id": session_id,
            "hostname": payload.hostname,
            "username": payload.username,
            "classroom_id": payload.classroom_id,
            "consent": True,
            "last_seen": storage.now_iso(),
            "session_started": storage.now_iso(),
            "metrics": None,
        }
        await storage.save_clients(clients)

        await storage.audit_log("register", actor=payload.device_id, ip=request.client.host if request.client else None, details={
            "hostname": payload.hostname,
            "username": payload.username,
            "classroom_id": payload.classroom_id,
        })

    return schemas.RegisterResponse(session_id=session_id)

@app.post("/api/v1/heartbeat")
async def heartbeat(payload: schemas.HeartbeatRequest, request: Request, _: str = Depends(require_api_key)) -> Dict[str, str]:
    if USE_DB_SERVICE:
        success = await db_service.update_client_metrics(
            device_id=payload.device_id,
            session_id=payload.session_id,
            metrics=payload.metrics.model_dump()
        )
        
        if not success:
            raise HTTPException(status_code=401, detail="Unknown device or invalid session")
    else:
        # Fallback to JSON storage
        clients = await storage.load_clients()
        client = clients.get(payload.device_id)

        if not client or client.get("session_id") != payload.session_id:
            raise HTTPException(status_code=401, detail="Unknown device or invalid session")

        client["metrics"] = payload.metrics.model_dump()
        client["last_seen"] = storage.now_iso()
        await storage.save_clients(clients)
    
    return {"status": "ok"}

@app.post("/api/v1/unregister")
async def unregister(payload: schemas.UnregisterRequest, request: Request, _: str = Depends(require_api_key)) -> Dict[str, str]:
    if USE_DB_SERVICE:
        success = await db_service.unregister_client(
            device_id=payload.device_id,
            session_id=payload.session_id,
            reason=payload.reason or "user_request"
        )
        
        if not success:
            await db_service.audit_log("unregister_mismatch", actor=payload.device_id, ip=request.client.host if request.client else None, details={"reason": payload.reason})
        else:
            await db_service.audit_log("unregister", actor=payload.device_id, ip=request.client.host if request.client else None, details={"reason": payload.reason})
    else:
        # Fallback to JSON storage
        clients = await storage.load_clients()
        client = clients.get(payload.device_id)

        if not client or client.get("session_id") != payload.session_id:
            await storage.audit_log("unregister_mismatch", actor=payload.device_id, ip=request.client.host if request.client else None, details={"reason": payload.reason})
            return {"status": "ok"}

        client["consent"] = False
        client["session_ended"] = storage.now_iso()
        await storage.save_clients(clients)

        await storage.audit_log("unregister", actor=payload.device_id, ip=request.client.host if request.client else None, details={"reason": payload.reason})
    
    return {"status": "ok"}

@app.get("/api/v1/clients")
async def list_clients(_: str = Depends(require_api_key)) -> Dict[str, Any]:
    return {"clients": await storage.load_clients()}

@app.get("/api/v1/clients/status", response_class=JSONResponse)
async def get_clients_status(_: str = Depends(require_api_key)) -> Dict[str, Any]:
    if USE_DB_SERVICE:
        return await db_service.get_clients_status()
    else:
        # Fallback to JSON storage
        clients_data = await storage.load_clients()
        now = datetime.now(timezone.utc)
        
        total = online = 0
        processed_clients: List[Dict[str, Any]] = []

        for device_id, client in clients_data.items():
            if not client.get("consent"):
                continue

            total += 1
            metrics = client.get("metrics", {}) or {}
            uptime = metrics.get("uptime_seconds", 0)
            
            last_seen_str = client.get("last_seen", "")
            status, status_class = "🔴 Desconectado", "offline"
            seconds_ago = 999
            try:
                last_dt = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                seconds_ago = (now - last_dt).total_seconds()
                if seconds_ago <= 60:
                    status, status_class = "🟢 En línea", "online"
                    online += 1
            except (ValueError, TypeError):
                pass

            h, rem = divmod(uptime, 3600)
            m, s = divmod(rem, 60)
            
            processed_clients.append({
                "id": device_id,
                "hostname": client.get('hostname', 'N/A'),
                "username": client.get('username', 'N/A'),
                "classroom": client.get('classroom_id', 'Sin aula'),
                "cpu": metrics.get("cpu_percent", 0),
                "mem": metrics.get("mem_percent", 0),
                "disk": metrics.get("disk_percent", 0),
                "uptime": uptime,
                "uptime_str": f"{int(h):02d}:{int(m):02d}:{int(s):02d}",
                "status": status,
                "status_class": status_class,
                "last_seen_seconds": int(seconds_ago)
            })

        stats = {
            "total": total,
            "online": online,
            "offline": total - online,
            "connectivity_percentage": round((online / total * 100) if total > 0 else 0)
        }
        return {"stats": stats, "clients": processed_clients}

# --- Dashboard Frontend ---
@app.get("/", response_class=HTMLResponse)
async def root_redirect():
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, api_key: Optional[str] = Query(None)):
    if not verify_api_key_optional(api_key):
        return templates.TemplateResponse("login.html", {"request": request, "default_api_key": settings.EDUMON_API_KEY})

    return templates.TemplateResponse("dashboard.html", {"request": request, "api_key": api_key})