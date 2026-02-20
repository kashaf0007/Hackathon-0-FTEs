"""
Gmail watcher - Monitors Gmail inbox for new emails.
Uses Gmail API with OAuth2 authentication.
"""

import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from AI_Employee_Vault.Watchers.watcher_base import WatcherBase


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailWatcher(WatcherBase):
    """
    Gmail watcher using Gmail API with OAuth2 authentication.

    Monitors Gmail inbox for new emails and creates event files.
    """

    def __init__(self, poll_interval: int = 600):
        """
        Initialize Gmail watcher.

        Args:
            poll_interval: Polling interval in seconds (default: 600 = 10 minutes)
        """
        super().__init__(source='gmail', poll_interval=poll_interval)

        self.credentials_file = Path('AI_Employee_Vault/Watchers/gmail_credentials.json')
        self.token_file = Path('AI_Employee_Vault/Watchers/gmail_token.json')
        self.service = None
        self.last_history_id = None

        # Authenticate on initialization
        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with Gmail API using OAuth2."""
        creds = None

        # Load existing token
        if self.token_file.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired token
                creds.refresh(Request())
            else:
                # Run OAuth2 flow
                if not self.credentials_file.exists():
                    raise FileNotFoundError(
                        f"Gmail credentials file not found: {self.credentials_file}\n"
                        "Please download OAuth2 credentials from Google Cloud Console."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token for future use
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        # Build Gmail service
        self.service = build('gmail', 'v1', credentials=creds)

        self.logger.info(
            component="watcher",
            action="authenticated",
            actor="gmail_watcher",
            target="gmail_api",
            details={"status": "success"}
        )

    def _get_message_details(self, message_id: str) -> Dict[str, Any]:
        """
        Get full message details from Gmail API.

        Args:
            message_id: Gmail message ID

        Returns:
            Message details dictionary
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract headers
            headers = {h['name']: h['value'] for h in message['payload']['headers']}

            # Extract body
            body = ''
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        import base64
                        body = base64.urlsafe_b64decode(part['body'].get('data', '')).decode('utf-8')
                        break
            elif 'body' in message['payload']:
                import base64
                body = base64.urlsafe_b64decode(message['payload']['body'].get('data', '')).decode('utf-8')

            return {
                'message_id': message_id,
                'thread_id': message.get('threadId'),
                'subject': headers.get('Subject', ''),
                'from': headers.get('From', ''),
                'to': headers.get('To', ''),
                'date': headers.get('Date', ''),
                'body': body,
                'labels': message.get('labelIds', []),
                'snippet': message.get('snippet', '')
            }

        except Exception as e:
            self.logger.error(
                component="watcher",
                action="fetch_message_failed",
                actor="gmail_watcher",
                target=message_id,
                details={"error": str(e)}
            )
            return {}

    def fetch_new_events(self) -> List[Dict[str, Any]]:
        """
        Fetch new emails from Gmail.

        Returns:
            List of raw event dictionaries
        """
        if not self.service:
            self._authenticate()

        events = []

        try:
            # Get unread messages
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD'],
                maxResults=10
            ).execute()

            messages = results.get('messages', [])

            for message in messages:
                message_details = self._get_message_details(message['id'])

                if not message_details:
                    continue

                # Determine contact history
                from_email = message_details.get('from', '')
                contact_history = self._determine_contact_history(from_email)

                # Determine priority based on labels and content
                priority = 'medium'
                if 'IMPORTANT' in message_details.get('labels', []):
                    priority = 'high'
                elif 'CATEGORY_PROMOTIONS' in message_details.get('labels', []):
                    priority = 'low'

                # Build raw event
                raw_event = {
                    'type': 'new_email',
                    'timestamp': datetime.now().isoformat() + 'Z',
                    'priority': priority,
                    'subject': message_details.get('subject', ''),
                    'body': message_details.get('body', ''),
                    'from': from_email,
                    'to': message_details.get('to', ''),
                    'attachments': [],
                    'metadata': {
                        'thread_id': message_details.get('thread_id'),
                        'labels': message_details.get('labels', []),
                        'is_reply': 'Re:' in message_details.get('subject', ''),
                        'contact_history': contact_history,
                        'raw_data': {
                            'message_id': message_details.get('message_id'),
                            'snippet': message_details.get('snippet', '')
                        }
                    }
                }

                events.append(raw_event)

        except Exception as e:
            self.logger.error(
                component="watcher",
                action="fetch_failed",
                actor="gmail_watcher",
                target="gmail_api",
                details={"error": str(e)}
            )

        return events

    def _determine_contact_history(self, email: str) -> str:
        """
        Determine contact history (new, known, frequent).

        Args:
            email: Email address

        Returns:
            Contact history: 'new', 'known', or 'frequent'
        """
        # Simple heuristic: check if we have previous events from this sender
        # In a real implementation, this would query a contact database
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
                    if event.get('content', {}).get('from') == email:
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
    """Run Gmail watcher in standalone mode."""
    import argparse

    parser = argparse.ArgumentParser(description='Gmail Watcher')
    parser.add_argument('--authenticate', action='store_true', help='Run authentication flow only')
    parser.add_argument('--test', action='store_true', help='Run one poll cycle and exit')
    parser.add_argument('--interval', type=int, default=600, help='Poll interval in seconds')

    args = parser.parse_args()

    watcher = GmailWatcher(poll_interval=args.interval)

    if args.authenticate:
        print("[OK] Authentication successful")
        return

    if args.test:
        print("Running test poll...")
        count = watcher.poll_once()
        print(f"[OK] Found {count} new events")
        return

    print(f"Starting Gmail watcher (polling every {args.interval} seconds)...")
    print("Press Ctrl+C to stop")
    watcher.run()


if __name__ == '__main__':
    main()
