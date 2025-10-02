#!/usr/bin/env python3
"""
Test the new Node.js server API endpoints
"""
import requests
import json

def test_server():
    """Test the server API endpoints"""
    base_url = "https://cae7ccde57d5.ngrok-free.app"
    
    print("Testing Node.js Server API")
    print("=" * 40)
    print(f"Base URL: {base_url}")
    
    # Test devices endpoint
    print("\nTesting GET /api/v1/devices...")
    try:
        response = requests.get(f"{base_url}/api/v1/devices", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test registration endpoint
    print("\nTesting POST /api/v1/register...")
    try:
        headers = {
            'X-API-Key': 'S1R4X',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "device_id": "test-device-123",
            "hostname": "test-computer",
            "username": "test-user",
            "consent": True,
            "classroom_id": "Aula-1"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/register",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return data.get('session_id')
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    return None

if __name__ == "__main__":
    test_server()