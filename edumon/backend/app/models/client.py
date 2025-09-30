"""
Client model for connected devices
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), unique=True, index=True, nullable=False)
    hostname = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    mac_address = Column(String(17), nullable=True)
    os_info = Column(String(200), nullable=True)
    consent_given = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Foreign keys
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True)

    # Relationships
    classroom = relationship("Classroom", back_populates="clients")
    sessions = relationship("Session", back_populates="client")
    metrics = relationship("Metrics", back_populates="client")

    def __repr__(self):
        return f"<Client(device_id='{self.device_id}', hostname='{self.hostname}')>"