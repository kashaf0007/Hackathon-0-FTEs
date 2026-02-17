"""
Email MCP Server - Handles email sending via SMTP with Gmail OAuth2.
Implements JSON-RPC 2.0 protocol for email operations.
"""

import os
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from mcp_servers.mcp_base import MCPServer


class EmailMCPServer(MCPServer):
    """
    MCP server for email operations using Gmail API.

    Supported methods:
    - send_email: Send an email message
    - get_status: Get email send status
    - validate_address: Validate email address format
    """

    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def __init__(self):
        """Initialize email MCP server."""
        super().__init__(server_name="email_server")
        self.credentials = None
        self.service = None
        self._authenticate()

    def _authenticate(self) -> None:
        """Authenticate with Gmail API using OAuth2."""
        token_file = 'gmail_token.json'
        creds_file = os.getenv('GMAIL_CREDENTIALS_FILE', 'gmail_credentials.json')

        # Load existing token
        if os.path.exists(token_file):
            self.credentials = Credentials.from_authorized_user_file(token_file, self.SCOPES)

        # Refresh or get new token
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                if not os.path.exists(creds_file):
                    self.logger.error(
                        component="mcp",
                        action="authentication_failed",
                        actor="email_server",
                        target="gmail_api",
                        details={"error": f"Credentials file not found: {creds_file}"}
                    )
                    raise FileNotFoundError(f"Gmail credentials file not found: {creds_file}")

                flow = InstalledAppFlow.from_client_secrets_file(creds_file, self.SCOPES)
                self.credentials = flow.run_local_server(port=0)

            # Save token
            with open(token_file, 'w') as token:
                token.write(self.credentials.to_json())

        # Build service
        self.service = build('gmail', 'v1', credentials=self.credentials)

        self.logger.info(
            component="mcp",
            action="authenticated",
            actor="email_server",
            target="gmail_api",
            details={"status": "success"}
        )

    def _execute_action(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute email action based on method.

        Args:
            method: Method name (send_email, get_status, validate_address)
            params: Method parameters

        Returns:
            Result dictionary

        Raises:
            ValueError: If method is unknown or params are invalid
        """
        if method == 'send_email':
            return self._send_email(params)
        elif method == 'get_status':
            return self._get_status(params)
        elif method == 'validate_address':
            return self._validate_address(params)
        else:
            raise ValueError(f"Unknown method: {method}")

    def _send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an email message.

        Args:
            params: Dictionary with:
                - to: Recipient email address (required)
                - subject: Email subject (required)
                - body: Email body text (required)
                - from_name: Sender name (optional)
                - cc: CC recipients list (optional)
                - bcc: BCC recipients list (optional)
                - html: Whether body is HTML (optional, default: False)

        Returns:
            Result with message_id and status

        Raises:
            ValueError: If required params missing
            HttpError: If Gmail API call fails
        """
        # Validate required params
        required = ['to', 'subject', 'body']
        for param in required:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")

        to = params['to']
        subject = params['subject']
        body = params['body']
        from_name = params.get('from_name', 'AI Employee')
        cc = params.get('cc', [])
        bcc = params.get('bcc', [])
        is_html = params.get('html', False)

        # Create message
        message = MIMEMultipart() if cc or bcc else MIMEText(body, 'html' if is_html else 'plain')

        if isinstance(message, MIMEMultipart):
            message.attach(MIMEText(body, 'html' if is_html else 'plain'))

        message['To'] = to
        message['Subject'] = subject
        message['From'] = from_name

        if cc:
            message['Cc'] = ', '.join(cc)
        if bcc:
            message['Bcc'] = ', '.join(bcc)

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        try:
            # Send via Gmail API
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            message_id = sent_message['id']

            self.logger.info(
                component="mcp",
                action="email_sent",
                actor="email_server",
                target=to,
                details={
                    "message_id": message_id,
                    "subject": subject,
                    "cc": cc,
                    "bcc": bcc
                }
            )

            return {
                'status': 'sent',
                'message_id': message_id,
                'to': to,
                'subject': subject
            }

        except HttpError as error:
            self.logger.error(
                component="mcp",
                action="email_send_failed",
                actor="email_server",
                target=to,
                details={
                    "error": str(error),
                    "subject": subject
                }
            )
            raise

    def _get_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get email send status.

        Args:
            params: Dictionary with:
                - message_id: Gmail message ID (required)

        Returns:
            Status information

        Raises:
            ValueError: If message_id missing
            HttpError: If Gmail API call fails
        """
        if 'message_id' not in params:
            raise ValueError("Missing required parameter: message_id")

        message_id = params['message_id']

        try:
            # Get message details
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['To', 'Subject', 'Date']
            ).execute()

            # Extract metadata
            headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}

            return {
                'status': 'delivered',
                'message_id': message_id,
                'to': headers.get('To', 'unknown'),
                'subject': headers.get('Subject', 'unknown'),
                'date': headers.get('Date', 'unknown'),
                'thread_id': message.get('threadId')
            }

        except HttpError as error:
            if error.resp.status == 404:
                return {
                    'status': 'not_found',
                    'message_id': message_id,
                    'error': 'Message not found'
                }
            raise

    def _validate_address(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate email address format.

        Args:
            params: Dictionary with:
                - email: Email address to validate (required)

        Returns:
            Validation result

        Raises:
            ValueError: If email param missing
        """
        if 'email' not in params:
            raise ValueError("Missing required parameter: email")

        email = params['email']

        # Basic email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = bool(re.match(email_pattern, email))

        return {
            'email': email,
            'valid': is_valid,
            'reason': 'Valid format' if is_valid else 'Invalid email format'
        }


def start_email_server(host: str = 'localhost', port: int = 5001):
    """
    Start the email MCP server.

    Args:
        host: Server host (default: localhost)
        port: Server port (default: 5001)
    """
    server = EmailMCPServer()
    print(f"Email MCP Server started on {host}:{port}")
    print("Supported methods: send_email, get_status, validate_address")
    print("Press Ctrl+C to stop")

    # Note: Actual server implementation would use a web framework
    # For now, this is a placeholder for the server startup
    # In production, use Flask, FastAPI, or similar


if __name__ == '__main__':
    start_email_server()
