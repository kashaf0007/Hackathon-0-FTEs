"""
WhatsApp watcher - Monitors WhatsApp for new messages.
Uses Node.js bridge with whatsapp-web.js for reliable session management.
"""

import os
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from AI_Employee_Vault.Watchers.watcher_base import WatcherBase


class WhatsAppWatcher(WatcherBase):
    """
    WhatsApp watcher using Node.js bridge with whatsapp-web.js.

    Monitors WhatsApp for:
    - Personal messages
    - Group messages (optional)

    Communicates with Node.js bridge server via HTTP API.
    """

    def __init__(self, poll_interval: int = 300, bridge_url: str = "http://localhost:5002"):
        """
        Initialize WhatsApp watcher.

        Args:
            poll_interval: Polling interval in seconds (default: 300 = 5 minutes)
            bridge_url: URL of Node.js bridge server
        """
        super().__init__(source='whatsapp', poll_interval=poll_interval)

        self.bridge_url = bridge_url.rstrip('/')
        self.session_ready = False
        self.personal_messages_enabled = True
        self.group_messages_enabled = False

        # Load configuration
        self._load_config()

        # Check bridge connectivity
        self._check_bridge()

    def _load_config(self) -> None:
        """Load WhatsApp-specific configuration from watcher_config.json."""
        import json
        config_file = Path('AI_Employee_Vault/Watchers/watcher_config.json')

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    whatsapp_config = config.get('watchers', {}).get('whatsapp', {})

                    # Update settings from config
                    self.bridge_url = whatsapp_config.get('bridge_url', self.bridge_url).rstrip('/')
                    features = whatsapp_config.get('features', {})
                    self.personal_messages_enabled = features.get('personal_messages', True)
                    self.group_messages_enabled = features.get('group_messages', False)
            except Exception as e:
                self.logger.warning(
                    component="watcher",
                    action="config_load_failed",
                    actor="whatsapp_watcher",
                    target="config",
                    details={"error": str(e)}
                )

    def _check_bridge(self) -> bool:
        """
        Check if Node.js bridge is running and ready.

        Returns:
            True if bridge is ready, False otherwise
        """
        try:
            response = requests.get(f"{self.bridge_url}/health", timeout=5)

            if response.status_code == 200:
                data = response.json()
                self.session_ready = data.get('ready', False)

                self.logger.info(
                    component="watcher",
                    action="bridge_check",
                    actor="whatsapp_watcher",
                    target="bridge",
                    details={
                        "status": "connected",
                        "ready": self.session_ready
                    }
                )

                return True
            else:
                self.logger.warning(
                    component="watcher",
                    action="bridge_check_failed",
                    actor="whatsapp_watcher",
                    target="bridge",
                    details={"status_code": response.status_code}
                )
                return False

        except requests.exceptions.RequestException as e:
            self.logger.error(
                component="watcher",
                action="bridge_unreachable",
                actor="whatsapp_watcher",
                target="bridge",
                details={
                    "error": str(e),
                    "bridge_url": self.bridge_url,
                    "hint": "Make sure Node.js bridge is running: node whatsapp_bridge.js"
                }
            )
            return False

    def _get_qr_code(self) -> Optional[str]:
        """
        Get QR code for WhatsApp authentication.

        Returns:
            QR code string if available, None otherwise
        """
        try:
            response = requests.get(f"{self.bridge_url}/qr", timeout=5)

            if response.status_code == 200:
                data = response.json()
                return data.get('qr')

            return None

        except Exception as e:
            self.logger.error(
                component="watcher",
                action="qr_fetch_failed",
                actor="whatsapp_watcher",
                target="bridge",
                details={"error": str(e)}
            )
            return None

    def _fetch_messages(self) -> List[Dict[str, Any]]:
        """
        Fetch new messages from WhatsApp via bridge.

        Returns:
            List of message dictionaries
        """
        try:
            response = requests.get(
                f"{self.bridge_url}/messages",
                params={
                    'personal': self.personal_messages_enabled,
                    'group': self.group_messages_enabled
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('messages', [])
            else:
                self.logger.warning(
                    component="watcher",
                    action="fetch_messages_failed",
                    actor="whatsapp_watcher",
                    target="bridge",
                    details={"status_code": response.status_code}
                )
                return []

        except requests.exceptions.RequestException as e:
            self.logger.error(
                component="watcher",
                action="fetch_messages_error",
                actor="whatsapp_watcher",
                target="bridge",
                details={"error": str(e)}
            )
            return []

    def _mark_message_processed(self, message_id: str) -> bool:
        """
        Mark message as processed in bridge.

        Args:
            message_id: Message ID to mark as processed

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.bridge_url}/mark-processed",
                json={'message_id': message_id},
                timeout=5
            )

            return response.status_code == 200

        except Exception:
            return False

    def fetch_new_events(self) -> List[Dict[str, Any]]:
        """
        Fetch new events from WhatsApp.

        Returns:
            List of raw event dictionaries
        """
        # Check bridge connectivity
        if not self._check_bridge():
            return []

        # If session not ready, check for QR code
        if not self.session_ready:
            qr = self._get_qr_code()
            if qr:
                self.logger.info(
                    component="watcher",
                    action="qr_code_available",
                    actor="whatsapp_watcher",
                    target="bridge",
                    details={
                        "message": "Scan QR code to authenticate WhatsApp",
                        "qr_length": len(qr)
                    }
                )
            return []

        # Fetch messages
        messages = self._fetch_messages()
        events = []

        for msg in messages:
            try:
                # Extract message details
                message_id = msg.get('id', '')
                from_contact = msg.get('from', '')
                body = msg.get('body', '')
                timestamp = msg.get('timestamp', datetime.now().isoformat() + 'Z')
                is_group = msg.get('isGroup', False)
                contact_name = msg.get('contactName', from_contact)

                # Determine priority
                priority = 'medium'
                if is_group:
                    priority = 'low'
                elif msg.get('isImportant', False):
                    priority = 'high'

                # Build raw event
                raw_event = {
                    'type': 'whatsapp_message',
                    'timestamp': timestamp,
                    'priority': priority,
                    'subject': f"WhatsApp from {contact_name}",
                    'body': body,
                    'from': contact_name,
                    'to': 'me',
                    'attachments': msg.get('attachments', []),
                    'metadata': {
                        'message_id': message_id,
                        'from_number': from_contact,
                        'is_group': is_group,
                        'group_name': msg.get('groupName', ''),
                        'contact_history': self._determine_contact_history(from_contact),
                        'has_media': msg.get('hasMedia', False),
                        'labels': ['whatsapp', 'group' if is_group else 'personal'],
                        'is_reply': False,
                        'raw_data': {
                            'chat_id': msg.get('chatId', ''),
                            'quoted_msg': msg.get('quotedMsg', None)
                        }
                    }
                }

                events.append(raw_event)

                # Mark as processed in bridge
                self._mark_message_processed(message_id)

            except Exception as e:
                self.logger.error(
                    component="watcher",
                    action="message_parse_failed",
                    actor="whatsapp_watcher",
                    target="message",
                    details={"error": str(e), "message": str(msg)}
                )
                continue

        return events

    def _determine_contact_history(self, contact: str) -> str:
        """
        Determine contact history (new, known, frequent).

        Args:
            contact: Contact identifier (phone number or name)

        Returns:
            Contact history: 'new', 'known', or 'frequent'
        """
        # Simple heuristic: check if we have previous events from this contact
        done_dir = Path('AI_Employee_Vault/Done')
        if not done_dir.exists():
            return 'new'

        # Count previous interactions
        count = 0
        for event_file in done_dir.glob('*.json'):
            try:
                import json
                with open(event_file, 'r') as f:
                    event = json.load(f)
                    metadata = event.get('metadata', {})
                    if metadata.get('from_number') == contact:
                        count += 1
            except Exception:
                continue

        if count == 0:
            return 'new'
        elif count < 5:
            return 'known'
        else:
            return 'frequent'


def main():
    """Run WhatsApp watcher in standalone mode."""
    import argparse

    parser = argparse.ArgumentParser(description='WhatsApp Watcher')
    parser.add_argument('--test', action='store_true', help='Run one poll cycle and exit')
    parser.add_argument('--interval', type=int, default=300, help='Poll interval in seconds')
    parser.add_argument('--bridge-url', default='http://localhost:5002', help='Node.js bridge URL')
    parser.add_argument('--check-bridge', action='store_true', help='Check bridge connectivity only')

    args = parser.parse_args()

    watcher = WhatsAppWatcher(poll_interval=args.interval, bridge_url=args.bridge_url)

    if args.check_bridge:
        if watcher._check_bridge():
            print(f"✓ Bridge connected (ready: {watcher.session_ready})")
            if not watcher.session_ready:
                qr = watcher._get_qr_code()
                if qr:
                    print("\n📱 Scan this QR code with WhatsApp:")
                    print(qr)
        else:
            print("✗ Bridge not reachable")
        return

    if args.test:
        print("Running test poll...")
        count = watcher.poll_once()
        print(f"✓ Found {count} new events")
        return

    print(f"Starting WhatsApp watcher (polling every {args.interval} seconds)...")
    print("Press Ctrl+C to stop")
    watcher.run()


if __name__ == '__main__':
    main()
