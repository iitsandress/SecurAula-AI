"""
Test configuration and fixtures
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.main import app


# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Create test database session"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Create test client"""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def api_headers():
    """API headers for testing"""
    return {"X-API-Key": "changeme"}


@pytest.fixture
def sample_client_data():
    """Sample client data for testing"""
    return {
        "device_id": "test-device-123",
        "hostname": "test-host",
        "username": "test-user",
        "consent": True,
        "classroom_id": 1,
        "ip_address": "192.168.1.100",
        "os_info": "Windows 10"
    }


@pytest.fixture
def sample_metrics_data():
    """Sample metrics data for testing"""
    return {
        "cpu_percent": 45.5,
        "memory_percent": 60.2,
        "memory_used": 8589934592,  # 8GB
        "memory_total": 17179869184,  # 16GB
        "uptime_seconds": 3600,
        "disk_percent": 75.0,
        "network_sent": 1024000,
        "network_recv": 2048000,
        "process_count": 150
    }