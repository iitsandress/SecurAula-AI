#!/usr/bin/env python3
"""
EduMon Agent - Configuration Update Script
Simple script to update the server URL in config.json
"""
import json
import os
import sys

def update_config():
    """Update the config.json file with a new server URL"""
    config_file = "config.json"
    
    print("🎓 EduMon Agent - Configuration Update")
    print("=" * 40)
    
    # Check if config.json exists
    if not os.path.exists(config_file):
        print(f"❌ Error: {config_file} not found!")
        print("Please make sure you're in the backup/edumon/agent directory")
        return False
    
    # Load current configuration
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error reading {config_file}: {e}")
        return False
    
    # Show current configuration
    print(f"\nCurrent configuration:")
    print(f"  Server URL: {config.get('server_url', 'Not set')}")
    print(f"  API Key: {config.get('api_key', 'Not set')}")
    
    # Get new server URL
    print("\n" + "=" * 40)
    print("Enter your ngrok URL (e.g., https://1234-5678-9abc-def0.ngrok-free.app)")
    print("Or press Enter to keep current URL")
    
    new_url = input("\nNgrok URL: ").strip()
    
    if new_url:
        # Validate URL format
        if not (new_url.startswith('http://') or new_url.startswith('https://')):
            print("⚠️  Warning: URL should start with http:// or https://")
            confirm = input("Continue anyway? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("❌ Configuration update cancelled")
                return False
        
        # Update configuration
        config['server_url'] = new_url
        
        # Save updated configuration
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print("\n✅ Configuration updated successfully!")
            print(f"   New server URL: {new_url}")
            print(f"   API Key: {config['api_key']}")
            
            print("\n🚀 You can now run the agent with:")
            print("   python main_simple.py")
            print("   or")
            print("   python main.py")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            return False
    else:
        print("ℹ️  No changes made to configuration")
        return True

def main():
    """Main function"""
    try:
        success = update_config()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n❌ Configuration update cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())