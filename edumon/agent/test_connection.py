#!/usr/bin/env python3
"""
EduMon Agent - Connection Test Script
Test the connection to the server without running the full agent
"""
import json
import os
import sys
import requests
from urllib.parse import urlparse

def test_connection():
    """Test connection to the configured server"""
    config_file = "config.json"
    
    print("🔍 EduMon Agent - Connection Test")
    print("=" * 40)
    
    # Check if config.json exists
    if not os.path.exists(config_file):
        print(f"❌ Error: {config_file} not found!")
        print("Please run update_config.py first")
        return False
    
    # Load configuration
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error reading {config_file}: {e}")
        return False
    
    server_url = config.get('server_url', '')
    api_key = config.get('api_key', '')
    
    print(f"Server URL: {server_url}")
    print(f"API Key: {api_key}")
    print()
    
    # Validate configuration
    if not server_url or server_url == "<YOUR_NGROK_URL>":
        print("❌ Error: Server URL not configured!")
        print("Please run update_config.py to set your ngrok URL")
        return False
    
    if not api_key:
        print("❌ Error: API Key not configured!")
        return False
    
    # Validate URL format
    try:
        parsed = urlparse(server_url)
        if not parsed.scheme or not parsed.netloc:
            print("❌ Error: Invalid server URL format!")
            return False
    except Exception:
        print("❌ Error: Invalid server URL format!")
        return False
    
    # Test connection
    print("🔗 Testing connection to server...")
    
    try:
        # Create session with headers
        session = requests.Session()
        session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'EduMon-Agent-Test/2.0.0'
        })
        
        # Try to connect to the root endpoint
        response = session.get(server_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Connection successful!")
            print(f"   Status: {response.status_code}")
            print(f"   Server responded successfully")
            
            # Try to get some basic info
            content_type = response.headers.get('content-type', '')
            if 'html' in content_type.lower():
                print("   Response: HTML page (likely the dashboard)")
            else:
                print(f"   Content-Type: {content_type}")
            
            return True
        else:
            print(f"⚠️  Server responded with status: {response.status_code}")
            print("   This might be normal if the server doesn't have a root endpoint")
            print("   The agent should still work for API endpoints")
            return True
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed: Cannot reach server")
        print("   Check that:")
        print("   - Your Node.js server is running")
        print("   - ngrok is active and forwarding to your server")
        print("   - The ngrok URL is correct")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Connection timeout: Server took too long to respond")
        return False
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    """Main function"""
    try:
        success = test_connection()
        
        if success:
            print("\n🚀 Configuration looks good! You can now run:")
            print("   python main_simple.py")
            print("   or")
            print("   python main.py")
        else:
            print("\n🔧 Please fix the configuration issues above")
            
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())