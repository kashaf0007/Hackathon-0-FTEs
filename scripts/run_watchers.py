#!/usr/bin/env python3
"""
Run all configured watchers.
Executes watchers based on watcher_config.json settings.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from AI_Employee_Vault.Watchers.gmail_watcher import GmailWatcher
from AI_Employee_Vault.Watchers.linkedin_watcher import LinkedInWatcher
from scripts.logger import get_logger


def load_config() -> Dict[str, Any]:
    """
    Load watcher configuration from watcher_config.json.

    Returns:
        Configuration dictionary
    """
    config_file = Path('AI_Employee_Vault/Watchers/watcher_config.json')

    if not config_file.exists():
        print(f"Error: Configuration file not found: {config_file}")
        sys.exit(1)

    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        sys.exit(1)


def run_watcher(watcher_name: str, watcher_config: Dict[str, Any], test_mode: bool = False) -> None:
    """
    Run a single watcher.

    Args:
        watcher_name: Name of watcher (gmail, linkedin, whatsapp)
        watcher_config: Watcher configuration dictionary
        test_mode: If True, run one poll cycle and exit
    """
    logger = get_logger()

    if not watcher_config.get('enabled', False):
        print(f"Skipping {watcher_name} watcher (disabled in config)")
        return

    poll_interval = watcher_config.get('poll_interval_seconds', 600)

    try:
        if watcher_name == 'gmail':
            watcher = GmailWatcher(poll_interval=poll_interval)
        elif watcher_name == 'linkedin':
            watcher = LinkedInWatcher(poll_interval=poll_interval)
        elif watcher_name == 'whatsapp':
            print(f"WhatsApp watcher not yet implemented")
            return
        else:
            print(f"Unknown watcher: {watcher_name}")
            return

        if test_mode:
            print(f"Testing {watcher_name} watcher...")
            count = watcher.poll_once()
            print(f"✓ {watcher_name}: Found {count} new events")
        else:
            print(f"Starting {watcher_name} watcher (interval: {poll_interval}s)")
            watcher.run(max_iterations=1)  # Run once per script execution

    except Exception as e:
        logger.error(
            component="watcher",
            action="watcher_failed",
            actor=f"{watcher_name}_watcher",
            target="run_watchers",
            details={"error": str(e)}
        )
        print(f"✗ {watcher_name} watcher failed: {e}")


def run_all_watchers(config: Dict[str, Any], test_mode: bool = False) -> None:
    """
    Run all enabled watchers.

    Args:
        config: Full configuration dictionary
        test_mode: If True, run one poll cycle per watcher and exit
    """
    watchers_config = config.get('watchers', {})

    for watcher_name, watcher_config in watchers_config.items():
        run_watcher(watcher_name, watcher_config, test_mode)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run AI Employee watchers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all enabled watchers once (for cron/scheduler)
  python scripts/run_watchers.py

  # Test all watchers
  python scripts/run_watchers.py --test

  # Run specific watcher
  python scripts/run_watchers.py --watcher gmail

  # Test specific watcher
  python scripts/run_watchers.py --watcher gmail --test
        """
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: run one poll cycle and exit'
    )

    parser.add_argument(
        '--watcher',
        choices=['gmail', 'linkedin', 'whatsapp'],
        help='Run specific watcher only'
    )

    parser.add_argument(
        '--config',
        default='AI_Employee_Vault/Watchers/watcher_config.json',
        help='Path to watcher configuration file'
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Check DRY_RUN mode
    dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
    if dry_run:
        print("⚠️  Running in DRY_RUN mode")

    # Run watchers
    if args.watcher:
        # Run specific watcher
        watcher_config = config.get('watchers', {}).get(args.watcher)
        if not watcher_config:
            print(f"Error: Watcher '{args.watcher}' not found in configuration")
            sys.exit(1)

        run_watcher(args.watcher, watcher_config, test_mode=args.test)
    else:
        # Run all watchers
        run_all_watchers(config, test_mode=args.test)

    print("\n✓ Watcher execution complete")


if __name__ == '__main__':
    main()
