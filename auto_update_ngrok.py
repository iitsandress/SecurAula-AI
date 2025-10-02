#!/usr/bin/env python3
"""
Auto-update agent config with current ngrok URL
"""
import json
import requests
import os

def get_ngrok_url():
    """Get current ngrok URL"""
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            if tunnels:
                return tunnels[0]['public_url']
    except:
        pass
    return None

def update_agent_config(ngrok_url):
    """Update agent configuration with new ngrok URL"""
    config_path = "backup/edumon/agent/config.json"
    
    try:
        # Read current config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update URL
        old_url = config.get('server_url', '')
        config['server_url'] = ngrok_url
        
        # Save config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration updated!")
        print(f"   Old URL: {old_url}")
        print(f"   New URL: {ngrok_url}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating config: {e}")
        return False

def main():
    """Main function"""
    print("🔍 Auto-detecting ngrok URL...")
    
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        print("❌ ngrok not found or not running")
        print("\nPlease:")
        print("1. Start ngrok: ngrok http 3000")
        print("2. Run this script again")
        return 1
    
    print(f"🔗 Found ngrok URL: {ngrok_url}")
    
    if update_agent_config(ngrok_url):
        print("\n🚀 Ready to run agent!")
        print("   python run_demo_agent.py")
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit(main())