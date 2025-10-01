#!/usr/bin/env python3
"""
Simple connection test script to verify server availability
"""
import requests
import json

def test_connection():
    """Test connection to the EduMon server"""
    print("🔍 Testing EduMon server connection...")
    
    try:
        # Load config
        with open('agent_config.json', 'r') as f:
            config = json.load(f)
        
        server_ip = config.get('server_ip', 'localhost')
        server_url = f"http://{server_ip}:8000"
        
        print(f"📡 Testing: {server_url}/health")
        
        response = requests.get(f"{server_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Connection test PASSED!")
            print(f"📊 Server response: {response.json()}")
            return True
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectTimeout:
        print("❌ Connection timeout - server is not reachable")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - server is not running")
        return False
    except FileNotFoundError:
        print("❌ agent_config.json not found!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        print("\n🎉 You can now run: python run_agent.py")
    else:
        print("\n🔧 Please start the server first:")
        print("   Option 1: python simple_backend.py")
        print("   Option 2: python run_server.py")