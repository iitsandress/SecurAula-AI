#!/usr/bin/env python3
"""
EduMon Fix Script - Complete Solution
This script will help you fix the connection issues and get EduMon working.
"""
import os
import sys
import json
import subprocess
import time
import requests
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.WHITE}🔧 EDUMON FIX SCRIPT{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.YELLOW}Fixing connection issues and setting up local server...{Colors.END}\n")

def check_docker():
    """Check if Docker is available"""
    print(f"{Colors.BLUE}🐳 Checking Docker...{Colors.END}")
    
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ Docker is installed{Colors.END}")
            
            # Check if Docker is running
            result = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Docker is running{Colors.END}")
                return True
            else:
                print(f"{Colors.YELLOW}⚠️  Docker is installed but not running{Colors.END}")
                print(f"{Colors.YELLOW}   Please start Docker Desktop and try again{Colors.END}")
                return False
        else:
            print(f"{Colors.RED}❌ Docker is not installed{Colors.END}")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print(f"{Colors.RED}❌ Docker is not available{Colors.END}")
        return False

def update_agent_config():
    """Update agent configuration to use localhost"""
    print(f"{Colors.BLUE}📝 Updating agent configuration...{Colors.END}")
    
    config_file = "agent_config.json"
    try:
        # Read current config
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Update to localhost
        config['server_ip'] = 'localhost'
        config['api_key'] = config.get('api_key', 'S1R4X')
        config['classroom_id'] = config.get('classroom_id', 'Aula-1')
        
        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"{Colors.GREEN}✅ Agent config updated to use localhost{Colors.END}")
        return True
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error updating config: {e}{Colors.END}")
        return False

def test_server_connection():
    """Test if the server is responding"""
    print(f"{Colors.BLUE}🔍 Testing server connection...{Colors.END}")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ Server is responding!{Colors.END}")
            data = response.json()
            print(f"   📊 Server version: {data.get('version', 'N/A')}")
            return True
        else:
            print(f"{Colors.YELLOW}⚠️  Server responded with status: {response.status_code}{Colors.END}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{Colors.YELLOW}⚠️  Server is not running on localhost:8000{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Connection test failed: {e}{Colors.END}")
        return False

def start_server_with_docker():
    """Start the server using Docker"""
    print(f"{Colors.BLUE}🚀 Starting server with Docker...{Colors.END}")
    print(f"{Colors.YELLOW}⏳ This may take a few minutes...{Colors.END}")
    
    try:
        # Run the automated server script
        result = subprocess.run([sys.executable, "run_server.py"], 
                              capture_output=False, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ Server started successfully!{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}❌ Server failed to start{Colors.END}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"{Colors.YELLOW}⚠️  Server startup timed out{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Error starting server: {e}{Colors.END}")
        return False

def show_manual_instructions():
    """Show manual setup instructions"""
    print(f"\n{Colors.CYAN}📋 MANUAL SETUP INSTRUCTIONS{Colors.END}")
    print(f"{Colors.CYAN}{'='*40}{Colors.END}")
    
    print(f"\n{Colors.YELLOW}Option 1: Start Server with Docker{Colors.END}")
    print(f"1. Make sure Docker Desktop is running")
    print(f"2. Run: {Colors.WHITE}python run_server.py{Colors.END}")
    print(f"3. Wait for all services to start")
    print(f"4. Run: {Colors.WHITE}python run_agent.py{Colors.END}")
    
    print(f"\n{Colors.YELLOW}Option 2: Simple Backend Only{Colors.END}")
    print(f"1. Install backend dependencies:")
    print(f"   {Colors.WHITE}cd edumon/backend{Colors.END}")
    print(f"   {Colors.WHITE}pip install -r requirements.txt{Colors.END}")
    print(f"2. Start backend:")
    print(f"   {Colors.WHITE}python -m uvicorn app.main:app --host 0.0.0.0 --port 8000{Colors.END}")
    print(f"3. In another terminal, run agent:")
    print(f"   {Colors.WHITE}python run_agent.py{Colors.END}")
    
    print(f"\n{Colors.YELLOW}Option 3: Use Remote Server{Colors.END}")
    print(f"1. Edit {Colors.WHITE}agent_config.json{Colors.END}")
    print(f"2. Change server_ip to the correct remote server IP")
    print(f"3. Make sure the remote server is accessible")

def main():
    print_header()
    
    # Step 1: Update agent config
    if not update_agent_config():
        print(f"{Colors.RED}❌ Failed to update agent configuration{Colors.END}")
        return 1
    
    # Step 2: Test if server is already running
    if test_server_connection():
        print(f"\n{Colors.GREEN}🎉 Server is already running!{Colors.END}")
        print(f"{Colors.GREEN}✅ You can now run the agent with: python run_agent.py{Colors.END}")
        return 0
    
    # Step 3: Check Docker availability
    docker_available = check_docker()
    
    if docker_available:
        print(f"\n{Colors.BLUE}🚀 Attempting to start server with Docker...{Colors.END}")
        
        # Try to start server
        if start_server_with_docker():
            # Test connection again
            time.sleep(10)  # Give server time to start
            if test_server_connection():
                print(f"\n{Colors.GREEN}🎉 SUCCESS! Server is now running!{Colors.END}")
                print(f"{Colors.GREEN}✅ You can now run the agent with: python run_agent.py{Colors.END}")
                return 0
    
    # If we get here, automatic setup failed
    print(f"\n{Colors.YELLOW}⚠️  Automatic setup failed or Docker is not available{Colors.END}")
    show_manual_instructions()
    
    print(f"\n{Colors.CYAN}🔧 Quick Test:{Colors.END}")
    print(f"Run: {Colors.WHITE}python test_connection.py{Colors.END} to test connectivity")
    
    return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Setup cancelled by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.END}")
        sys.exit(1)