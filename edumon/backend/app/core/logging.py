"""
Logging configuration and utilities
"""
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from .config import settings
from .database import SessionLocal
from ..models.audit_log import AuditLog


# Configure logging
def setup_logging():
    """Setup application logging"""
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(
        os.path.join(settings.LOG_DIR, 'edumon.log')
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger


class AuditLogger:
    """Audit logger for tracking system events"""
    
    @staticmethod
    def log_event(
        action: str,
        actor: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "info",
        user_id: Optional[int] = None,
        client_id: Optional[int] = None
    ):
        """Log an audit event to the database"""
        db = SessionLocal()
        try:
            audit_log = AuditLog(
                action=action,
                actor=actor,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details,
                severity=severity,
                user_id=user_id,
                client_id=client_id
            )
            db.add(audit_log)
            db.commit()
        except Exception as e:
            logging.error(f"Failed to log audit event: {e}")
            db.rollback()
        finally:
            db.close()
    
    @staticmethod
    def log_user_action(action: str, user_id: int, details: Optional[Dict[str, Any]] = None):
        """Log a user action"""
        AuditLogger.log_event(
            action=action,
            actor=f"user_{user_id}",
            user_id=user_id,
            details=details
        )
    
    @staticmethod
    def log_client_action(action: str, device_id: str, client_id: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        """Log a client action"""
        AuditLogger.log_event(
            action=action,
            actor=device_id,
            client_id=client_id,
            details=details
        )
    
    @staticmethod
    def log_system_action(action: str, details: Optional[Dict[str, Any]] = None):
        """Log a system action"""
        AuditLogger.log_event(
            action=action,
            actor="system",
            details=details
        )