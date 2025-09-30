"""
Session model for tracking client sessions
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    end_reason = Column(String(100), nullable=True)  # user_request, server_stop, timeout, etc.
    notes = Column(Text, nullable=True)

    # Foreign keys
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Teacher who started the session
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True)

    # Relationships
    client = relationship("Client", back_populates="sessions")
    user = relationship("User", back_populates="sessions")
    classroom = relationship("Classroom", back_populates="sessions")
    metrics = relationship("Metrics", back_populates="session")

    def __repr__(self):
        return f"<Session(session_id='{self.session_id}', client='{self.client.device_id if self.client else None}')>"