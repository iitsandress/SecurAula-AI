#!/usr/bin/env python3
"""
EduMon Agent - Main Entry Point
Educational monitoring agent with modern PyQt6 interface
"""
import sys
import os
import logging
import argparse
from typing import Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import load_config, save_config, AgentConfig
from core.logging_config import setup_logging


def setup_argument_parser() -> argparse.ArgumentParser:
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(
        description="EduMon Agent - Educational Monitoring System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with GUI
  python main.py --headless         # Run without GUI
  python main.py --config-wizard    # Run configuration wizard
  python main.py --version          # Show version
        """
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode (no GUI)"
    )
    
    parser.add_argument(
        "--config-wizard",
        action="store_true",
        help="Run configuration wizard"
    )
    
    parser.add_argument(
        "--config-file",
        type=str,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="EduMon Agent v2.0.0"
    )
    
    return parser


def run_config_wizard() -> AgentConfig:
    """Run configuration wizard"""
    print("=== EduMon Agent Configuration Wizard ===\n")
    
    config = AgentConfig()
    
    # Server configuration
    print("1. Server Configuration")
    server_url = input(f"Server URL [{config.server_url}]: ").strip()
    if server_url:
        config.server_url = server_url
    
    api_key = input(f"API Key [{config.api_key}]: ").strip()
    if api_key:
        config.api_key = api_key
    
    classroom_id = input(f"Classroom ID [{config.classroom_id or ''}]: ").strip()
    if classroom_id:
        config.classroom_id = classroom_id
    
    # Metrics configuration
    print("\n2. Metrics Configuration")
    collect_disk = input(f"Collect disk metrics? [{'y' if config.collect_disk_metrics else 'n'}]: ").strip().lower()
    if collect_disk in ['y', 'yes']:
        config.collect_disk_metrics = True
    elif collect_disk in ['n', 'no']:
        config.collect_disk_metrics = False
    
    collect_network = input(f"Collect network metrics? [{'y' if config.collect_network_metrics else 'n'}]: ").strip().lower()
    if collect_network in ['y', 'yes']:
        config.collect_network_metrics = True
    elif collect_network in ['n', 'no']:
        config.collect_network_metrics = False
    
    # Save configuration
    if save_config(config):
        print("\n✓ Configuration saved successfully!")
    else:
        print("\n✗ Failed to save configuration!")
    
    return config


def run_headless_mode(config: AgentConfig) -> int:
    """Run agent in headless mode"""
    try:
        from core.agent_core import AgentCore
        
        print("Starting EduMon Agent in headless mode...")
        print(f"Server: {config.server_url}")
        print(f"Classroom: {config.classroom_id or 'Not set'}")
        print("Press Ctrl+C to stop\n")
        
        agent = AgentCore(config)
        return agent.run()
        
    except KeyboardInterrupt:
        print("\nAgent stopped by user")
        return 0
    except Exception as e:
        logging.error(f"Error in headless mode: {e}")
        return 1


def run_gui_mode(config: AgentConfig) -> int:
    """Run agent with GUI"""
    try:
        # Check if PyQt6 is available
        try:
            from PyQt6.QtWidgets import QApplication
        except ImportError:
            print("PyQt6 not available. Running in headless mode...")
            return run_headless_mode(config)
        
        from ui.main_window import main as gui_main
        
        return gui_main()
        
    except Exception as e:
        logging.error(f"Error in GUI mode: {e}")
        print(f"GUI failed to start: {e}")
        print("Falling back to headless mode...")
        return run_headless_mode(config)


def main() -> int:
    """Main entry point"""
    # Parse command line arguments
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level=args.log_level)
    
    # Load configuration
    try:
        if args.config_file:
            # TODO: Load from specific file
            config = load_config()
        else:
            config = load_config()
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        print(f"Error loading configuration: {e}")
        return 1
    
    # Run configuration wizard if requested
    if args.config_wizard:
        config = run_config_wizard()
        if not args.headless:
            print("\nConfiguration complete. Starting agent...")
    
    # Validate configuration
    if not config.api_key or config.api_key == "por-favor-cambie-esta-clave":
        print("ERROR: Please configure a valid API key")
        print("Run with --config-wizard to set up configuration")
        return 1
    
    # Run agent
    try:
        if args.headless:
            return run_headless_mode(config)
        else:
            return run_gui_mode(config)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())