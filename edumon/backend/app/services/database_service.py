"""
Database service that handles both SQLAlchemy and JSON storage
"""
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..core.database import get_db, engine
from ..models.client import Client
from ..models.session import Session as SessionModel
from ..models.metrics import Metrics
from ..models.classroom import Classroom
from ..models.audit_log import AuditLog
from ..core.config import settings
from .storage import load_clients, save_clients, audit_log as json_audit_log


class DatabaseService:
    """Hybrid database service supporting both SQLAlchemy and JSON"""
    
    def __init__(self):
        self.use_database = self._check_database_available()
    
    def _check_database_available(self) -> bool:
        """Check if database is available"""
        try:
            # Try to connect to database
            db = next(get_db())
            db.execute("SELECT 1")
            db.close()
            return True
        except Exception:
            return False
    
    async def register_client(self, device_id: str, hostname: str, username: str, 
                            classroom_id: Optional[str], ip_address: Optional[str] = None) -> str:
        """Register a new client"""
        session_id = f"session_{device_id}_{int(datetime.now().timestamp())}"
        
        if self.use_database:
            try:
                db = next(get_db())
                
                # Find or create classroom
                classroom = None
                if classroom_id:
                    classroom = db.query(Classroom).filter(Classroom.name == classroom_id).first()
                    if not classroom:
                        classroom = Classroom(name=classroom_id, description=f"Auto-created classroom {classroom_id}")
                        db.add(classroom)
                        db.flush()  # Flush to get the ID without committing
                        db.refresh(classroom)
                
                # Find or create client
                client = db.query(Client).filter(Client.device_id == device_id).first()
                if not client:
                    client = Client(
                        device_id=device_id,
                        hostname=hostname,
                        username=username,
                        ip_address=ip_address,
                        classroom_id=classroom.id if classroom else None,
                        consent_given=True,
                        is_online=True
                    )
                    db.add(client)
                else:
                    client.hostname = hostname
                    client.username = username
                    client.ip_address = ip_address
                    client.classroom_id = classroom.id if classroom else None
                    client.consent_given = True
                    client.is_online = True
                    client.last_seen = datetime.now(timezone.utc)
                
                # Create session
                session = SessionModel(
                    session_id=session_id,
                    client_id=client.id,
                    classroom_id=classroom.id if classroom else None,
                    is_active=True
                )
                db.add(session)
                
                db.commit()
                db.close()
                
            except SQLAlchemyError as e:
                print(f"Database error, falling back to JSON: {e}")
                self.use_database = False
        
        if not self.use_database:
            # Fallback to JSON storage
            clients = await load_clients()
            clients[device_id] = {
                "session_id": session_id,
                "hostname": hostname,
                "username": username,
                "classroom_id": classroom_id,
                "consent": True,
                "last_seen": datetime.now(timezone.utc).isoformat(),
                "session_started": datetime.now(timezone.utc).isoformat(),
                "metrics": None,
            }
            await save_clients(clients)
        
        return session_id
    
    async def update_client_metrics(self, device_id: str, session_id: str, metrics: Dict[str, Any]) -> bool:
        """Update client metrics"""
        if self.use_database:
            try:
                db = next(get_db())
                
                # Find client and session
                client = db.query(Client).filter(Client.device_id == device_id).first()
                session = db.query(SessionModel).filter(
                    SessionModel.session_id == session_id,
                    SessionModel.client_id == client.id if client else None
                ).first()
                
                if not client or not session:
                    db.close()
                    return False
                
                # Update client last seen
                client.last_seen = datetime.now(timezone.utc)
                client.is_online = True
                
                # Create metrics record
                metrics_record = Metrics(
                    client_id=client.id,
                    session_id=session.id,
                    cpu_percent=metrics.get("cpu_percent", 0),
                    memory_percent=metrics.get("mem_percent", 0),
                    disk_percent=metrics.get("disk_percent"),
                    uptime_seconds=metrics.get("uptime_seconds", 0),
                    network_sent=metrics.get("network_sent"),
                    network_recv=metrics.get("network_recv"),
                    process_count=metrics.get("process_count")
                )
                db.add(metrics_record)
                
                db.commit()
                db.close()
                return True
                
            except SQLAlchemyError as e:
                print(f"Database error, falling back to JSON: {e}")
                self.use_database = False
        
        if not self.use_database:
            # Fallback to JSON storage
            clients = await load_clients()
            client = clients.get(device_id)
            
            if not client or client.get("session_id") != session_id:
                return False
            
            client["metrics"] = metrics
            client["last_seen"] = datetime.now(timezone.utc).isoformat()
            await save_clients(clients)
            return True
    
    async def unregister_client(self, device_id: str, session_id: str, reason: str = "user_request") -> bool:
        """Unregister a client"""
        if self.use_database:
            try:
                db = next(get_db())
                
                # Find client and session
                client = db.query(Client).filter(Client.device_id == device_id).first()
                session = db.query(SessionModel).filter(
                    SessionModel.session_id == session_id,
                    SessionModel.client_id == client.id if client else None
                ).first()
                
                if client:
                    client.is_online = False
                    client.consent_given = False
                
                if session:
                    session.is_active = False
                    session.end_time = datetime.now(timezone.utc)
                    session.end_reason = reason
                
                db.commit()
                db.close()
                return True
                
            except SQLAlchemyError as e:
                print(f"Database error, falling back to JSON: {e}")
                self.use_database = False
        
        if not self.use_database:
            # Fallback to JSON storage
            clients = await load_clients()
            client = clients.get(device_id)
            
            if not client or client.get("session_id") != session_id:
                return True  # Already unregistered
            
            client["consent"] = False
            client["session_ended"] = datetime.now(timezone.utc).isoformat()
            await save_clients(clients)
            return True
    
    async def get_clients_status(self) -> Dict[str, Any]:
        """Get current clients status"""
        if self.use_database:
            try:
                db = next(get_db())
                
                # Get active clients with their latest metrics
                clients = db.query(Client).filter(Client.consent_given == True).all()
                
                processed_clients = []
                total = online = 0
                now = datetime.now(timezone.utc)
                
                for client in clients:
                    total += 1
                    
                    # Get latest metrics
                    latest_metrics = db.query(Metrics).filter(
                        Metrics.client_id == client.id
                    ).order_by(Metrics.timestamp.desc()).first()
                    
                    # Check if online (last seen within 60 seconds)
                    seconds_ago = 999
                    status = "🔴 Desconectado"
                    status_class = "offline"
                    
                    if client.last_seen:
                        seconds_ago = (now - client.last_seen).total_seconds()
                        if seconds_ago <= 60:
                            status = "🟢 En línea"
                            status_class = "online"
                            online += 1
                    
                    # Format uptime
                    uptime = latest_metrics.uptime_seconds if latest_metrics else 0
                    h, rem = divmod(uptime, 3600)
                    m, s = divmod(rem, 60)
                    
                    processed_clients.append({
                        "id": client.device_id,
                        "hostname": client.hostname,
                        "username": client.username,
                        "classroom": client.classroom.name if client.classroom else "Sin aula",
                        "cpu": latest_metrics.cpu_percent if latest_metrics else 0,
                        "mem": latest_metrics.memory_percent if latest_metrics else 0,
                        "disk": latest_metrics.disk_percent if latest_metrics else 0,
                        "uptime": uptime,
                        "uptime_str": f"{int(h):02d}:{int(m):02d}:{int(s):02d}",
                        "status": status,
                        "status_class": status_class,
                        "last_seen_seconds": int(seconds_ago)
                    })
                
                db.close()
                
                stats = {
                    "total": total,
                    "online": online,
                    "offline": total - online,
                    "connectivity_percentage": round((online / total * 100) if total > 0 else 0)
                }
                
                return {"stats": stats, "clients": processed_clients}
                
            except SQLAlchemyError as e:
                print(f"Database error, falling back to JSON: {e}")
                self.use_database = False
        
        if not self.use_database:
            # Fallback to JSON storage (existing implementation)
            clients_data = await load_clients()
            now = datetime.now(timezone.utc)
            
            total = online = 0
            processed_clients = []
            
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
    
    async def audit_log(self, action: str, actor: str, ip: Optional[str] = None, 
                       details: Optional[Dict[str, Any]] = None) -> None:
        """Log audit event"""
        if self.use_database:
            try:
                db = next(get_db())
                
                audit_entry = AuditLog(
                    action=action,
                    actor=actor,
                    ip_address=ip,
                    details=details or {}
                )
                db.add(audit_entry)
                db.commit()
                db.close()
                return
                
            except SQLAlchemyError as e:
                print(f"Database error, falling back to JSON: {e}")
                self.use_database = False
        
        if not self.use_database:
            # Fallback to JSON audit log
            await json_audit_log(action, actor, ip, details)


# Global instance
db_service = DatabaseService()