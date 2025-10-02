"""
Agent configuration management
"""
import json
import os
import sys
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class AgentConfig:
    """Agent configuration"""
    server_url: str = "http://127.0.0.1:8000"
    api_key: str = ""
    heartbeat_seconds: int = 15
    classroom_id: Optional[str] = None
    auto_start: bool = False
    minimize_to_tray: bool = True
    enable_notifications: bool = True
    log_level: str = "INFO"
    
    # Advanced metrics
    collect_disk_metrics: bool = True
    collect_network_metrics: bool = True
    collect_process_metrics: bool = True
    collect_temperature: bool = False
    
    # Security
    verify_ssl: bool = True
    timeout_seconds: int = 10


def get_base_dir() -> str:
    """Get base directory for the agent"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(__file__))


def load_config() -> AgentConfig:
    """Load configuration from file"""
    base_dir = get_base_dir()
    config_path = os.path.join(base_dir, 'config.json')
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return AgentConfig(**data)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Try to load example config
    example_path = os.path.join(base_dir, 'config.example.json')
    if os.path.exists(example_path):
        try:
            with open(example_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return AgentConfig(**data)
        except Exception:
            pass
    
    return AgentConfig()


def save_config(config: AgentConfig) -> bool:
    """Save configuration to file"""
    try:
        base_dir = get_base_dir()
        config_path = os.path.join(base_dir, 'config.json')
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(config), f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False