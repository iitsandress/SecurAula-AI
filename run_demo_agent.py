#!/usr/bin/env python3
"""
Demo script to run the EduMon agent automatically
"""
import sys
import os

# Add the agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backup', 'edumon', 'agent'))

# Import the agent
from main_windows import SimpleAgent

class DemoAgent(SimpleAgent):
    """Demo agent that automatically gives consent"""
    
    def get_consent(self) -> bool:
        """Automatically give consent for demo"""
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
        print("\nAUTO-CONSENT: YES (Demo mode)")
        return True

def main():
    """Main function"""
    print("EduMon Agent - Demo Mode")
    print("=" * 40)
    
    # Change to agent directory
    agent_dir = os.path.join(os.path.dirname(__file__), 'backup', 'edumon', 'agent')
    os.chdir(agent_dir)
    
    agent = DemoAgent()
    return agent.run()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nDemo stopped by user")
        sys.exit(0)