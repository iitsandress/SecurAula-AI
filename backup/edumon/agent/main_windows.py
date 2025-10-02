#!/usr/bin/env python3
"""
EduMon Agent - Windows Compatible Version
Educational monitoring agent without Unicode characters
"""
import os
import sys
import json
import time
import uuid
import socket
import getpass
import requests
import psutil
from datetime import datetime
from typing import Dict, Any, Optional

# Default configuration
DEFAULT_CONFIG = {
    "server_url": "http://190.84.119.196:8000",
    "api_key": "S1R4X",
    "classroom_id": "Aula-1",
    "heartbeat_seconds": 15,
    "collect_disk_metrics": True,
    "collect_network_metrics": True,
    "collect_process_metrics": True,
    "verify_ssl": False,
    "timeout_seconds": 10
}

class SimpleAgent:
    """Simple agent without GUI and Unicode characters"""
    
    def __init__(self):
        self.config = self.load_config()
        self.device_id = self.get_device_id()
        self.session_id = None
        self.running = False
        
        # Configure requests
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.config['api_key'],
            'Content-Type': 'application/json',
            'User-Agent': 'EduMon-Agent-Simple/2.0.0'
        })
        
        if not self.config.get('verify_ssl', True):
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        config_file = "config.json"
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Combine with default values
                result = DEFAULT_CONFIG.copy()
                result.update(config)
                return result
            except Exception as e:
                print(f"Error loading configuration: {e}")
        
        # Create default configuration
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
            print("Configuration created with default values")
        except Exception as e:
            print(f"Could not create configuration: {e}")
        
        return DEFAULT_CONFIG.copy()
    
    def get_device_id(self) -> str:
        """Get unique device ID"""
        device_file = "device_id.txt"
        
        if os.path.exists(device_file):
            try:
                with open(device_file, 'r') as f:
                    return f.read().strip()
            except:
                pass
        
        # Generate new ID
        device_id = str(uuid.uuid4())
        try:
            with open(device_file, 'w') as f:
                f.write(device_id)
        except:
            pass
        
        return device_id
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics"""
        try:
            # Basic metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            
            metrics = {
                "cpu_percent": round(cpu_percent, 1),
                "mem_percent": round(memory.percent, 1),
                "uptime_seconds": int(uptime)
            }
            
            # Additional metrics if enabled
            if self.config.get('collect_disk_metrics', True):
                disk = psutil.disk_usage('/')
                metrics["disk_percent"] = round(disk.percent, 1)
            
            if self.config.get('collect_network_metrics', True):
                net_io = psutil.net_io_counters()
                metrics["network_sent"] = net_io.bytes_sent
                metrics["network_recv"] = net_io.bytes_recv
            
            if self.config.get('collect_process_metrics', True):
                metrics["process_count"] = len(psutil.pids())
            
            return metrics
            
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            return {
                "cpu_percent": 0.0,
                "mem_percent": 0.0,
                "uptime_seconds": 0
            }
    
    def get_consent(self) -> bool:
        """Request user consent"""
        print("\n" + "="*60)
        print("EDUMON - CONSENT FOR EDUCATIONAL MONITORING")
        print("="*60)
        print("\nThis agent will send ONLY the following data:")
        print("- Anonymous device identifier")
        print("- Host name and system user")
        print("- Performance metrics: CPU, RAM, disk, network")
        print("- System uptime")
        print("- Process information (names only)")
        print("\nNEVER captured:")
        print("- Screenshots")
        print("- Keystrokes")
        print("- File contents")
        print("- Browsing history")
        print("- Personal data")
        print("\nYou can stop monitoring at any time with Ctrl+C")
        print("="*60)
        
        while True:
            response = input("\nDo you accept to participate in this monitoring session? (yes/no): ").strip().lower()
            if response in ['yes', 'y', 'si', 's']:
                return True
            elif response in ['no', 'n']:
                return False
            else:
                print("Please answer 'yes' or 'no'")
    
    def register_with_server(self) -> bool:
        """Register with server"""
        try:
            payload = {
                "device_id": self.device_id,
                "hostname": socket.gethostname(),
                "username": getpass.getuser(),
                "consent": True,
                "classroom_id": self.config.get('classroom_id')
            }
            
            print(f"Connecting to server: {self.config['server_url']}")
            
            response = self.session.post(
                f"{self.config['server_url']}/api/v1/register",
                json=payload,
                timeout=self.config.get('timeout_seconds', 10)
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data["session_id"]
                print(f"Registration successful. Session ID: {self.session_id}")
                return True
            else:
                print(f"Registration error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat with metrics"""
        try:
            if not self.session_id:
                return False
            
            metrics = self.get_system_metrics()
            
            payload = {
                "device_id": self.device_id,
                "session_id": self.session_id,
                "metrics": metrics
            }
            
            response = self.session.post(
                f"{self.config['server_url']}/api/v1/heartbeat",
                json=payload,
                timeout=self.config.get('timeout_seconds', 10)
            )
            
            if response.status_code == 200:
                print(f"Metrics sent - CPU: {metrics['cpu_percent']}% RAM: {metrics['mem_percent']}%")
                return True
            else:
                print(f"Error sending metrics: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Heartbeat error: {e}")
            return False
    
    def unregister_from_server(self, reason: str = "user_request") -> bool:
        """Unregister from server"""
        try:
            if not self.session_id:
                return True
            
            payload = {
                "device_id": self.device_id,
                "session_id": self.session_id,
                "reason": reason
            }
            
            response = self.session.post(
                f"{self.config['server_url']}/api/v1/unregister",
                json=payload,
                timeout=self.config.get('timeout_seconds', 10)
            )
            
            if response.status_code == 200:
                print("Unregistration successful")
                return True
            else:
                print(f"Unregistration error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error unregistering: {e}")
            return False
    
    def run(self) -> int:
        """Run the agent"""
        try:
            print("EduMon Agent - Simple Version")
            print("=" * 40)
            
            # Request consent
            if not self.get_consent():
                print("Consent not granted")
                return 0
            
            # Register with server
            if not self.register_with_server():
                print("Could not connect to server")
                return 1
            
            # Show information
            print("\nAGENT STARTED")
            print("=" * 40)
            print(f"Device ID: {self.device_id}")
            print(f"Server: {self.config['server_url']}")
            print(f"Classroom: {self.config.get('classroom_id', 'Not configured')}")
            print(f"Interval: {self.config.get('heartbeat_seconds', 15)} seconds")
            print("\nPress Ctrl+C to stop")
            print("=" * 40)
            print()
            
            # Main loop
            self.running = True
            heartbeat_interval = self.config.get('heartbeat_seconds', 15)
            
            while self.running:
                try:
                    # Send heartbeat
                    if not self.send_heartbeat():
                        print("Heartbeat failed, continuing...")
                    
                    # Wait
                    time.sleep(heartbeat_interval)
                    
                except KeyboardInterrupt:
                    break
            
            # Unregister
            self.unregister_from_server("user_interrupt")
            
            print("\nAgent stopped correctly")
            return 0
            
        except Exception as e:
            print(f"Error running agent: {e}")
            return 1
        finally:
            self.running = False

def main():
    """Main function"""
    agent = SimpleAgent()
    return agent.run()

if __name__ == "__main__":
    sys.exit(main())