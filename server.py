from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import uvicorn
from datetime import datetime, timezone

app = FastAPI()

# In-memory data store
clients: Dict[str, Dict[str, Any]] = {}

class RegisterRequest(BaseModel):
    device_id: str
    hostname: str
    username: str
    consent: bool
    classroom_id: Optional[str] = None
    os_info: Optional[str] = None

class HeartbeatRequest(BaseModel):
    device_id: str
    session_id: str
    metrics: Dict[str, Any]

class UnregisterRequest(BaseModel):
    device_id: str
    session_id: str
    reason: Optional[str] = None

@app.post("/api/v1/register")
async def register(payload: RegisterRequest, request: Request):
    if not payload.consent:
        raise HTTPException(status_code=400, detail="Consent is required")

    session_id = str(request.client.host)
    clients[payload.device_id] = {
        "session_id": session_id,
        "hostname": payload.hostname,
        "username": payload.username,
        "classroom_id": payload.classroom_id,
        "consent": True,
        "last_seen": datetime.now(timezone.utc).isoformat(),
        "session_started": datetime.now(timezone.utc).isoformat(),
        "metrics": None,
        "screenshot": None,
    }
    return {"session_id": session_id}

@app.post("/api/v1/heartbeat")
async def heartbeat(payload: HeartbeatRequest):
    client = clients.get(payload.device_id)
    if not client or client.get("session_id") != payload.session_id:
        raise HTTPException(status_code=401, detail="Unknown device or invalid session")

    client["metrics"] = payload.metrics
    client["last_seen"] = datetime.now(timezone.utc).isoformat()
    return {"status": "ok"}

@app.post("/api/v1/unregister")
async def unregister(payload: UnregisterRequest):
    client = clients.get(payload.device_id)
    if not client or client.get("session_id") != payload.session_id:
        return {"status": "ok"}

    client["consent"] = False
    client["session_ended"] = datetime.now(timezone.utc).isoformat()
    return {"status": "ok"}

@app.get("/api/v1/clients/status", response_class=JSONResponse)
async def get_clients_status():
    now = datetime.now(timezone.utc)
    total = online = 0
    processed_clients: List[Dict[str, Any]] = []

    for device_id, client in clients.items():
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

@app.post("/api/v1/clients/{device_id}/screenshot_request")
async def request_screenshot(device_id: str):
    client = clients.get(device_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client["screenshot_request"] = True
    return {"status": "ok"}

@app.get("/api/v1/clients/{device_id}/screenshot")
async def get_screenshot(device_id: str):
    client = clients.get(device_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    # This endpoint will be polled by the dashboard
    # The agent will upload the screenshot to the client object
    if client.get("screenshot"):
        return {"screenshot": client.pop("screenshot")}
    else:
        return {"screenshot": None}

@app.post("/api/v1/clients/{device_id}/screenshot")
async def upload_screenshot(device_id: str, request: Request):
    client = clients.get(device_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    data = await request.json()
    client["screenshot"] = data.get("screenshot")
    return {"status": "ok"}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    with open("dashboard.html", "r") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)