#!/usr/bin/env python3
"""
Test the agent connection without user interaction
"""
import json
import uuid
import socket
import getpass
import requests
import psutil
import time

def test_agent():
    """Test agent functionality"""
    print("EduMon Agent - Connection Test")
    print("=" * 40)
    
    # Load config
    with open("config.json", 'r') as f:
        config = json.load(f)
    
    print(f"Server: {config['server_url']}")
    print(f"API Key: {config['api_key']}")
    
    # Create session
    session = requests.Session()
    session.headers.update({
        'X-API-Key': config['api_key'],
        'Content-Type': 'application/json',
        'User-Agent': 'EduMon-Agent-Test/2.0.0'
    })
    
    # Generate device ID
    device_id = str(uuid.uuid4())
    
    # Test registration
    print("\nTesting registration...")
    payload = {
        "device_id": device_id,
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "consent": True,
        "classroom_id": config.get('classroom_id')
    }
    
    try:
        response = session.post(
            f"{config['server_url']}/api/v1/register",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data["session_id"]
            print(f"Registration successful! Session ID: {session_id}")
            
            # Test heartbeat
            print("Testing heartbeat...")
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            metrics = {
                "cpu_percent": round(cpu_percent, 1),
                "mem_percent": round(memory.percent, 1),
                "uptime_seconds": 3600
            }
            
            heartbeat_payload = {
                "device_id": device_id,
                "session_id": session_id,
                "metrics": metrics
            }
            
            response = session.post(
                f"{config['server_url']}/api/v1/heartbeat",
                json=heartbeat_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Heartbeat successful! CPU: {metrics['cpu_percent']}% RAM: {metrics['mem_percent']}%")
                
                # Test unregister
                print("Testing unregistration...")
                unregister_payload = {
                    "device_id": device_id,
                    "session_id": session_id,
                    "reason": "test_complete"
                }
                
                response = session.post(
                    f"{config['server_url']}/api/v1/unregister",
                    json=unregister_payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print("Unregistration successful!")
                    print("\nALL TESTS PASSED!")
                    print("The agent is ready to run.")
                    return True
                else:
                    print(f"Unregistration failed: {response.status_code}")
            else:
                print(f"Heartbeat failed: {response.status_code}")
        else:
            print(f"Registration failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Test failed: {e}")
        return False
    
    return False

if __name__ == "__main__":
    success = test_agent()
    if not success:
        print("\nSome tests failed. Check your configuration and server.")