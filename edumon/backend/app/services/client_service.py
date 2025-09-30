"""
Client service for managing connected devices
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..models.client import Client
from ..models.session import Session as ClientSession
from ..models.classroom import Classroom
from ..core.logging import AuditLogger


class ClientService:
    """Service for managing clients"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_client_by_device_id(self, device_id: str) -> Optional[Client]:
        """Get client by device ID"""
        return self.db.query(Client).filter(Client.device_id == device_id).first()
    
    def create_or_update_client(
        self,
        device_id: str,
        hostname: str,
        username: str,
        ip_address: Optional[str] = None,
        mac_address: Optional[str] = None,
        os_info: Optional[str] = None,
        classroom_id: Optional[int] = None
    ) -> Client:
        """Create or update a client"""
        client = self.get_client_by_device_id(device_id)
        
        if client:
            # Update existing client
            client.hostname = hostname
            client.username = username
            client.ip_address = ip_address
            client.mac_address = mac_address
            client.os_info = os_info
            if classroom_id:
                client.classroom_id = classroom_id
            client.updated_at = datetime.now(timezone.utc)
            client.last_seen = datetime.now(timezone.utc)
            client.is_online = True
        else:
            # Create new client
            client = Client(
                device_id=device_id,
                hostname=hostname,
                username=username,
                ip_address=ip_address,
                mac_address=mac_address,
                os_info=os_info,
                classroom_id=classroom_id,
                is_online=True,
                last_seen=datetime.now(timezone.utc)
            )
            self.db.add(client)
        
        self.db.commit()
        self.db.refresh(client)
        
        AuditLogger.log_client_action(
            action="client_updated" if client.id else "client_created",
            device_id=device_id,
            client_id=client.id,
            details={
                "hostname": hostname,
                "username": username,
                "classroom_id": classroom_id
            }
        )
        
        return client
    
    def update_client_status(self, device_id: str, is_online: bool) -> Optional[Client]:
        """Update client online status"""
        client = self.get_client_by_device_id(device_id)
        if client:
            client.is_online = is_online
            client.last_seen = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(client)
        return client
    
    def get_online_clients(self, classroom_id: Optional[int] = None) -> List[Client]:
        """Get all online clients, optionally filtered by classroom"""
        query = self.db.query(Client).filter(Client.is_online == True)
        if classroom_id:
            query = query.filter(Client.classroom_id == classroom_id)
        return query.all()
    
    def get_clients_by_classroom(self, classroom_id: int) -> List[Client]:
        """Get all clients in a classroom"""
        return self.db.query(Client).filter(Client.classroom_id == classroom_id).all()
    
    def cleanup_offline_clients(self, timeout_minutes: int = 5) -> int:
        """Mark clients as offline if they haven't been seen recently"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
        
        offline_clients = self.db.query(Client).filter(
            and_(
                Client.is_online == True,
                Client.last_seen < cutoff_time
            )
        ).all()
        
        count = 0
        for client in offline_clients:
            client.is_online = False
            count += 1
            
            AuditLogger.log_client_action(
                action="client_timeout",
                device_id=client.device_id,
                client_id=client.id,
                details={"timeout_minutes": timeout_minutes}
            )
        
        if count > 0:
            self.db.commit()
        
        return count
    
    def get_client_statistics(self) -> Dict[str, Any]:
        """Get client statistics"""
        total_clients = self.db.query(Client).count()
        online_clients = self.db.query(Client).filter(Client.is_online == True).count()
        
        # Clients by classroom
        classroom_stats = self.db.query(
            Classroom.name,
            self.db.query(Client).filter(
                and_(
                    Client.classroom_id == Classroom.id,
                    Client.is_online == True
                )
            ).count().label('online_count')
        ).all()
        
        return {
            "total_clients": total_clients,
            "online_clients": online_clients,
            "offline_clients": total_clients - online_clients,
            "classroom_stats": [
                {"classroom": stat.name, "online_count": stat.online_count}
                for stat in classroom_stats
            ]
        }