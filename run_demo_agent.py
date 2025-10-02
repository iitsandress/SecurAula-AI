#!/usr/bin/env python3
"""
Demo script to run the EduMon agent automatically (auto-consent)
"""

import sys
import os

# Ensure repository root is on sys.path so we can import package-style
repo_root = os.path.abspath(os.path.dirname(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Import the simple agent implementation that exists in SERVIDOR FINAL/agent
# We import using package/module path to avoid fragile sys.path hacks.
from agent.main_simple import SimpleAgent


class DemoAgent(SimpleAgent):
    """Demo agent that automatically gives consent"""

    def get_consent(self) -> bool:
        """Automatically give consent for demo"""
        print("\n" + "=" * 60)
        print("EDUMON - CONSENT FOR EDUCATIONAL MONITORING (DEMO AUTO-CONSENT)")
        print("=" * 60)
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
        print("=" * 60)
        print("\nAUTO-CONSENT: YES (Demo mode)")
        return True


def main():
    """Main function"""
    print("EduMon Agent - Demo Mode")
    print("=" * 40)

    # Change to the actual agent directory to let the agent read/write device_id/config.json there
    agent_dir = os.path.join(repo_root, 'SERVIDOR FINAL', 'agent')
    if os.path.isdir(agent_dir):
        os.chdir(agent_dir)
    else:
        # fallback: try top-level agent folder if structure differs
        alt_agent = os.path.join(repo_root, 'agent')
        if os.path.isdir(alt_agent):
            os.chdir(alt_agent)

    agent = DemoAgent()
    return agent.run()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nDemo stopped by user")
        sys.exit(0)