"""
Client management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from ...core.database import get_db
from ...core.security import verify_api_key
from ...core.logging import AuditLogger
from ...services.client_service import ClientService
from ...services.session_service import SessionService
from ...models.client import Client

router = APIRouter()


# Pydantic models
class ClientRegisterRequest(BaseModel):
    device_id: str = Field(..., min_length=4, max_length=200)
    hostname: str = Field(..., min_length=1, max_length=200)
    username: str = Field(..., min_length=1, max_length=200)
    consent: bool
    classroom_id: Optional[int] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    os_info: Optional[str] = None


class ClientRegisterResponse(BaseModel):
    session_id: str
    client_id: int


class MetricsData(BaseModel):
    cpu_percent: float = Field(..., ge=0, le=100)
    memory_percent: float = Field(..., ge=0, le=100)
    memory_used: Optional[int] = None
    memory_total: Optional[int] = None
    disk_percent: Optional[float] = Field(None, ge=0, le=100)
    disk_used: Optional[int] = None
    disk_total: Optional[int] = None
    uptime_seconds: int = Field(..., ge=0)
    network_sent: Optional[int] = None
    network_recv: Optional[int] = None
    process_count: Optional[int] = None
    active_window: Optional[str] = None
    load_average: Optional[float] = None
    temperature: Optional[float] = None


class HeartbeatRequest(BaseModel):
    device_id: str
    session_id: str
    metrics: MetricsData


class UnregisterRequest(BaseModel):
    device_id: str
    session_id: str
    reason: Optional[str] = None


@router.post("/register", response_model=ClientRegisterResponse)
async def register_client(
    payload: ClientRegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
):
    """Register a new client device"""
    if not payload.consent:
        raise HTTPException(status_code=400, detail="Consent is required")
    
    client_service = ClientService(db)
    session_service = SessionService(db)
    
    # Get client IP from request
    client_ip = request.client.host if request.client else None
    
    # Create or update client
    client = client_service.create_or_update_client(
        device_id=payload.device_id,
        hostname=payload.hostname,
        username=payload.username,
        ip_address=payload.ip_address or client_ip,
        mac_address=payload.mac_address,
        os_info=payload.os_info,
        classroom_id=payload.classroom_id
    )
    
    # Update consent
    client.consent_given = True
    db.commit()
    
    # Create session
    session = session_service.create_session(
        client_id=client.id,
        classroom_id=payload.classroom_id
    )
    
    AuditLogger.log_client_action(
        action="client_registered",
        device_id=payload.device_id,
        client_id=client.id,
        details={
            "hostname": payload.hostname,
            "username": payload.username,
            "classroom_id": payload.classroom_id,
            "ip_address": client_ip
        }
    )
    
    return ClientRegisterResponse(
        session_id=session.session_id,
        client_id=client.id
    )


@router.post("/heartbeat")
async def client_heartbeat(
    payload: HeartbeatRequest,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
):
    """Receive heartbeat from client with metrics"""
    client_service = ClientService(db)
    session_service = SessionService(db)
    
    # Verify client and session
    client = client_service.get_client_by_device_id(payload.device_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    session = session_service.get_session_by_id(payload.session_id)
    if not session or not session.is_active or session.client_id != client.id:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Update client status
    client_service.update_client_status(payload.device_id, True)
    
    # Store metrics (we'll implement this in metrics service)
    from ...services.metrics_service import MetricsService
    metrics_service = MetricsService(db)
    metrics_service.store_metrics(
        client_id=client.id,
        session_id=session.id,
        metrics_data=payload.metrics.dict()
    )
    
    return {"status": "ok"}


@router.post("/unregister")
async def unregister_client(
    payload: UnregisterRequest,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
):
    """Unregister a client device"""
    client_service = ClientService(db)
    session_service = SessionService(db)
    
    # Verify client
    client = client_service.get_client_by_device_id(payload.device_id)
    if not client:
        # Idempotent response
        return {"status": "ok"}
    
    # End session
    session = session_service.get_session_by_id(payload.session_id)
    if session and session.is_active and session.client_id == client.id:
        session_service.end_session(payload.session_id, payload.reason or "client_request")
    
    # Update client status
    client.consent_given = False
    client_service.update_client_status(payload.device_id, False)
    
    AuditLogger.log_client_action(
        action="client_unregistered",
        device_id=payload.device_id,
        client_id=client.id,
        details={"reason": payload.reason}
    )
    
    return {"status": "ok"}


@router.get("/")
async def list_clients(
    classroom_id: Optional[int] = None,
    online_only: bool = False,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
):
    """List all clients with optional filters"""
    client_service = ClientService(db)
    
    if online_only:
        clients = client_service.get_online_clients(classroom_id)
    elif classroom_id:
        clients = client_service.get_clients_by_classroom(classroom_id)
    else:
        query = db.query(Client)
        if classroom_id:
            query = query.filter(Client.classroom_id == classroom_id)
        clients = query.all()
    
    return {"clients": clients}


@router.get("/statistics")
async def get_client_statistics(
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key)
):
    """Get client statistics"""
    client_service = ClientService(db)
    return client_service.get_client_statistics()