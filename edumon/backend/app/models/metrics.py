"""
Metrics model for storing system metrics
"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Metrics(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # System metrics
    cpu_percent = Column(Float, nullable=False)
    memory_percent = Column(Float, nullable=False)
    memory_used = Column(BigInteger, nullable=True)  # bytes
    memory_total = Column(BigInteger, nullable=True)  # bytes
    disk_percent = Column(Float, nullable=True)
    disk_used = Column(BigInteger, nullable=True)  # bytes
    disk_total = Column(BigInteger, nullable=True)  # bytes
    uptime_seconds = Column(Integer, nullable=False)
    
    # Network metrics
    network_sent = Column(BigInteger, nullable=True)  # bytes
    network_recv = Column(BigInteger, nullable=True)  # bytes
    
    # Process metrics
    process_count = Column(Integer, nullable=True)
    active_window = Column(String(200), nullable=True)
    
    # Performance metrics
    load_average = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)  # CPU temperature if available

    # Foreign keys
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)

    # Relationships
    client = relationship("Client", back_populates="metrics")
    session = relationship("Session", back_populates="metrics")

    def __repr__(self):
        return f"<Metrics(client='{self.client.device_id if self.client else None}', cpu={self.cpu_percent}%, mem={self.memory_percent}%)>"