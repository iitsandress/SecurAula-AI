"""
Tests for client API endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestClientAPI:
    """Test client API endpoints"""
    
    def test_register_client_success(self, client: TestClient, api_headers, sample_client_data):
        """Test successful client registration"""
        response = client.post("/api/v1/clients/register", json=sample_client_data, headers=api_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "client_id" in data
        assert isinstance(data["session_id"], str)
        assert isinstance(data["client_id"], int)
    
    def test_register_client_no_consent(self, client: TestClient, api_headers, sample_client_data):
        """Test client registration without consent"""
        sample_client_data["consent"] = False
        response = client.post("/api/v1/clients/register", json=sample_client_data, headers=api_headers)
        
        assert response.status_code == 400
        assert "consent" in response.json()["detail"].lower()
    
    def test_register_client_no_api_key(self, client: TestClient, sample_client_data):
        """Test client registration without API key"""
        response = client.post("/api/v1/clients/register", json=sample_client_data)
        
        assert response.status_code == 401
    
    def test_register_client_invalid_data(self, client: TestClient, api_headers):
        """Test client registration with invalid data"""
        invalid_data = {
            "device_id": "",  # Too short
            "hostname": "",   # Too short
            "username": "",   # Too short
            "consent": True
        }
        
        response = client.post("/api/v1/clients/register", json=invalid_data, headers=api_headers)
        assert response.status_code == 422
    
    def test_heartbeat_success(self, client: TestClient, api_headers, sample_client_data, sample_metrics_data):
        """Test successful heartbeat"""
        # First register a client
        register_response = client.post("/api/v1/clients/register", json=sample_client_data, headers=api_headers)
        assert register_response.status_code == 200
        session_data = register_response.json()
        
        # Send heartbeat
        heartbeat_data = {
            "device_id": sample_client_data["device_id"],
            "session_id": session_data["session_id"],
            "metrics": sample_metrics_data
        }
        
        response = client.post("/api/v1/clients/heartbeat", json=heartbeat_data, headers=api_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_heartbeat_invalid_session(self, client: TestClient, api_headers, sample_client_data, sample_metrics_data):
        """Test heartbeat with invalid session"""
        # Register client first
        register_response = client.post("/api/v1/clients/register", json=sample_client_data, headers=api_headers)
        assert register_response.status_code == 200
        
        # Send heartbeat with invalid session
        heartbeat_data = {
            "device_id": sample_client_data["device_id"],
            "session_id": "invalid-session-id",
            "metrics": sample_metrics_data
        }
        
        response = client.post("/api/v1/clients/heartbeat", json=heartbeat_data, headers=api_headers)
        assert response.status_code == 401
    
    def test_unregister_client_success(self, client: TestClient, api_headers, sample_client_data):
        """Test successful client unregistration"""
        # Register client first
        register_response = client.post("/api/v1/clients/register", json=sample_client_data, headers=api_headers)
        assert register_response.status_code == 200
        session_data = register_response.json()
        
        # Unregister client
        unregister_data = {
            "device_id": sample_client_data["device_id"],
            "session_id": session_data["session_id"],
            "reason": "test_completion"
        }
        
        response = client.post("/api/v1/clients/unregister", json=unregister_data, headers=api_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_unregister_nonexistent_client(self, client: TestClient, api_headers):
        """Test unregistering non-existent client (should be idempotent)"""
        unregister_data = {
            "device_id": "nonexistent-device",
            "session_id": "nonexistent-session",
            "reason": "test"
        }
        
        response = client.post("/api/v1/clients/unregister", json=unregister_data, headers=api_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_list_clients(self, client: TestClient, api_headers, sample_client_data):
        """Test listing clients"""
        # Register a client first
        client.post("/api/v1/clients/register", json=sample_client_data, headers=api_headers)
        
        # List clients
        response = client.get("/api/v1/clients/", headers=api_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "clients" in data
        assert isinstance(data["clients"], list)
        assert len(data["clients"]) >= 1
    
    def test_client_statistics(self, client: TestClient, api_headers, sample_client_data):
        """Test client statistics endpoint"""
        # Register a client first
        client.post("/api/v1/clients/register", json=sample_client_data, headers=api_headers)
        
        # Get statistics
        response = client.get("/api/v1/clients/statistics", headers=api_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_clients" in data
        assert "online_clients" in data
        assert "offline_clients" in data
        assert isinstance(data["total_clients"], int)
        assert data["total_clients"] >= 1