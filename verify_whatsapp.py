#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Integration Verification Script

Verifies that all WhatsApp components are properly configured and functional.
"""

import json
import os
import sys
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False

def check_node_modules():
    """Check if Node.js dependencies are installed."""
    if Path('node_modules').exists():
        print("✅ Node.js dependencies installed")
        return True
    else:
        print("❌ Node.js dependencies not installed. Run: npm install")
        return False

def check_watcher_config():
    """Check WhatsApp configuration in watcher_config.json."""
    config_file = Path('AI_Employee_Vault/Watchers/watcher_config.json')

    if not config_file.exists():
        print("❌ watcher_config.json not found")
        return False

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)

        whatsapp_config = config.get('watchers', {}).get('whatsapp', {})

        if not whatsapp_config:
            print("❌ WhatsApp configuration missing in watcher_config.json")
            return False

        enabled = whatsapp_config.get('enabled', False)
        bridge_url = whatsapp_config.get('bridge_url', '')

        print(f"✅ WhatsApp watcher configuration found")
        print(f"   - Enabled: {enabled}")
        print(f"   - Bridge URL: {bridge_url}")

        if not enabled:
            print("   ⚠️  WhatsApp watcher is disabled. Set 'enabled': true to activate.")

        return True

    except Exception as e:
        print(f"❌ Error reading watcher_config.json: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has WhatsApp configuration."""
    env_file = Path('.env')

    if not env_file.exists():
        print("⚠️  .env file not found. Copy .env.example to .env and configure.")
        return False

    try:
        with open(env_file, 'r') as f:
            content = f.read()

        has_whatsapp_config = 'WHATSAPP' in content

        if has_whatsapp_config:
            print("✅ WhatsApp configuration found in .env")
        else:
            print("⚠️  WhatsApp configuration not found in .env")

        return has_whatsapp_config

    except Exception as e:
        print(f"❌ Error reading .env: {e}")
        return False

def check_gitignore():
    """Check if .gitignore includes WhatsApp session files."""
    gitignore_file = Path('.gitignore')

    if not gitignore_file.exists():
        print("⚠️  .gitignore not found")
        return False

    try:
        with open(gitignore_file, 'r') as f:
            content = f.read()

        has_session = '.wwebjs_auth' in content
        has_node_modules = 'node_modules' in content

        if has_session and has_node_modules:
            print("✅ .gitignore properly configured for WhatsApp")
        else:
            print("⚠️  .gitignore may need updates:")
            if not has_session:
                print("   - Add: .wwebjs_auth/")
            if not has_node_modules:
                print("   - Add: node_modules/")

        return has_session and has_node_modules

    except Exception as e:
        print(f"❌ Error reading .gitignore: {e}")
        return False

def test_bridge_connectivity():
    """Test if WhatsApp bridge is reachable."""
    try:
        import requests

        # Try to connect to bridge
        response = requests.get('http://localhost:5002/health', timeout=2)

        if response.status_code == 200:
            data = response.json()
            ready = data.get('ready', False)

            print(f"✅ WhatsApp bridge is running")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Ready: {ready}")
            print(f"   - Unprocessed messages: {data.get('unprocessed_count', 0)}")

            if not ready:
                print("   ⚠️  Bridge not authenticated. Scan QR code to authenticate.")

            return True
        else:
            print(f"⚠️  Bridge responded with status {response.status_code}")
            return False

    except ImportError:
        print("⚠️  'requests' library not installed. Cannot test bridge connectivity.")
        return None
    except Exception as e:
        print(f"⚠️  WhatsApp bridge not reachable: {e}")
        print("   Start the bridge with: node whatsapp_bridge.js")
        return False

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("WhatsApp Integration Verification")
    print("=" * 60)
    print()

    checks = []

    # File existence checks
    print("📁 Checking files...")
    checks.append(check_file_exists('whatsapp_bridge.js', 'WhatsApp bridge server'))
    checks.append(check_file_exists('package.json', 'Node.js package configuration'))
    checks.append(check_file_exists('AI_Employee_Vault/Watchers/whatsapp_watcher.py', 'WhatsApp watcher'))
    checks.append(check_file_exists('WHATSAPP_SETUP.md', 'Setup documentation'))
    print()

    # Node.js dependencies
    print("📦 Checking Node.js dependencies...")
    checks.append(check_node_modules())
    print()

    # Configuration checks
    print("⚙️  Checking configuration...")
    checks.append(check_watcher_config())
    checks.append(check_env_file())
    checks.append(check_gitignore())
    print()

    # Bridge connectivity
    print("🌐 Checking bridge connectivity...")
    bridge_status = test_bridge_connectivity()
    if bridge_status is not None:
        checks.append(bridge_status)
    print()

    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)

    passed = sum(1 for c in checks if c)
    total = len(checks)

    print(f"Checks passed: {passed}/{total}")
    print()

    if passed == total:
        print("✅ All checks passed! WhatsApp integration is ready.")
        print()
        print("Next steps:")
        print("1. Start the bridge: node whatsapp_bridge.js")
        print("2. Scan QR code with WhatsApp (if not authenticated)")
        print("3. Test the watcher: python scripts/run_watchers.py --watcher whatsapp --test")
        return 0
    else:
        print("⚠️  Some checks failed. Review the output above and fix issues.")
        print()
        print("Common fixes:")
        print("- Install Node.js dependencies: npm install")
        print("- Copy .env.example to .env and configure")
        print("- Enable WhatsApp in watcher_config.json")
        print("- Start the bridge: node whatsapp_bridge.js")
        return 1

if __name__ == '__main__':
    sys.exit(main())
