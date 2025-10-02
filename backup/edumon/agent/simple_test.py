#!/usr/bin/env python3
"""
Simple connection test without Unicode characters
"""
import json
import requests

def test_connection():
    """Test connection to the configured server"""
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
        
        server_url = config.get('server_url', '')
        api_key = config.get('api_key', '')
        
        print("EduMon Agent - Connection Test")
        print("=" * 40)
        print(f"Server URL: {server_url}")
        print(f"API Key: {api_key}")
        print()
        
        if not server_url or server_url == "<YOUR_NGROK_URL>":
            print("ERROR: Server URL not configured!")
            return False
        
        print("Testing connection...")
        
        session = requests.Session()
        session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'EduMon-Agent-Test/2.0.0'
        })
        
        response = session.get(server_url, timeout=10)
        
        if response.status_code == 200:
            print("SUCCESS: Connection successful!")
            print(f"Status: {response.status_code}")
            return True
        else:
            print(f"Server responded with status: {response.status_code}")
            return True
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot reach server")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\nConfiguration looks good!")
        print("You can now run: python main_simple.py")
    else:
        print("\nPlease check the configuration")