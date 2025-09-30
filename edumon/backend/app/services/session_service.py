"""
Session service for managing client sessions
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import and_
from ..models.session import Session
from ..models.client import Client
from ..core.logging import AuditLogger


class SessionService:
    """Service for managing client sessions"""
    
    def __init__(self, db: DBSession):
        self.db = db
    
    def create_session(
        self,
        client_id: int,
        user_id: Optional[int] = None,
        classroom_id: Optional[int] = None
    ) -> Session:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        
        # End any existing active sessions for this client
        self.end_client_sessions(client_id, "new_session_started")
        
        session = Session(
            session_id=session_id,
            client_id=client_id,
            user_id=user_id,
            classroom_id=classroom_id,
            is_active=True
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        AuditLogger.log_client_action(
            action="session_created",
            device_id=session.client.device_id if session.client else "unknown",
            client_id=client_id,
            details={
                "session_id": session_id,
                "user_id": user_id,
                "classroom_id": classroom_id
            }
        )
        
        return session
    
    def get_session_by_id(self, session_id: str) -> Optional[Session]:
        """Get session by session ID"""
        return self.db.query(Session).filter(Session.session_id == session_id).first()
    
    def get_active_session_by_client(self, client_id: int) -> Optional[Session]:
        """Get active session for a client"""
        return self.db.query(Session).filter(
            and_(
                Session.client_id == client_id,
                Session.is_active == True
            )
        ).first()
    
    def end_session(
        self,
        session_id: str,
        reason: str = "user_request"
    ) -> Optional[Session]:
        """End a session"""
        session = self.get_session_by_id(session_id)
        if session and session.is_active:
            session.is_active = False
            session.end_time = datetime.now(timezone.utc)
            session.end_reason = reason
            
            self.db.commit()
            self.db.refresh(session)
            
            AuditLogger.log_client_action(
                action="session_ended",
                device_id=session.client.device_id if session.client else "unknown",
                client_id=session.client_id,
                details={
                    "session_id": session_id,
                    "reason": reason,
                    "duration_seconds": (
                        session.end_time - session.start_time
                    ).total_seconds() if session.end_time else None
                }
            )
        
        return session
    
    def end_client_sessions(self, client_id: int, reason: str = "client_disconnect") -> int:
        """End all active sessions for a client"""
        sessions = self.db.query(Session).filter(
            and_(
                Session.client_id == client_id,
                Session.is_active == True
            )
        ).all()
        
        count = 0
        for session in sessions:
            session.is_active = False
            session.end_time = datetime.now(timezone.utc)
            session.end_reason = reason
            count += 1
        
        if count > 0:
            self.db.commit()
        
        return count
    
    def get_active_sessions(self, classroom_id: Optional[int] = None) -> List[Session]:
        """Get all active sessions, optionally filtered by classroom"""
        query = self.db.query(Session).filter(Session.is_active == True)
        if classroom_id:
            query = query.filter(Session.classroom_id == classroom_id)
        return query.all()
    
    def get_session_history(
        self,
        client_id: Optional[int] = None,
        user_id: Optional[int] = None,
        classroom_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Session]:
        """Get session history with optional filters"""
        query = self.db.query(Session)
        
        if client_id:
            query = query.filter(Session.client_id == client_id)
        if user_id:
            query = query.filter(Session.user_id == user_id)
        if classroom_id:
            query = query.filter(Session.classroom_id == classroom_id)
        
        return query.order_by(Session.start_time.desc()).limit(limit).all()
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics"""
        total_sessions = self.db.query(Session).count()
        active_sessions = self.db.query(Session).filter(Session.is_active == True).count()
        
        # Average session duration (for completed sessions)
        completed_sessions = self.db.query(Session).filter(
            and_(
                Session.is_active == False,
                Session.end_time.isnot(None)
            )
        ).all()
        
        avg_duration = 0
        if completed_sessions:
            total_duration = sum([
                (session.end_time - session.start_time).total_seconds()
                for session in completed_sessions
            ])
            avg_duration = total_duration / len(completed_sessions)
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": len(completed_sessions),
            "average_duration_seconds": avg_duration
        }