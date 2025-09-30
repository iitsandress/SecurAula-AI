from pydantic import BaseModel, Field
from typing import Optional

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
    disk_percent: Optional[float] = Field(default=None, ge=0, le=100)
    network_sent: Optional[int] = Field(default=None, ge=0)
    network_recv: Optional[int] = Field(default=None, ge=0)
    process_count: Optional[int] = Field(default=None, ge=0)

class HeartbeatRequest(BaseModel):
    device_id: str
    session_id: str
    metrics: Metrics

class UnregisterRequest(BaseModel):
    device_id: str
    session_id: str
    reason: Optional[str] = None
