"""
MCP Client - Client wrapper for calling MCP servers via JSON-RPC 2.0.
Provides simple interface for executing actions on MCP servers.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

from scripts.logger import get_logger


class MCPClient:
    """
    Client for calling MCP servers.

    Provides a simple interface for executing actions on MCP servers
    without needing to handle JSON-RPC protocol details.
    """

    def __init__(self, dry_run: Optional[bool] = None):
        """
        Initialize MCP client.

        Args:
            dry_run: If True, simulate calls without real execution
        """
        self.dry_run = dry_run if dry_run is not None else (
            os.getenv('DRY_RUN', 'true').lower() == 'true'
        )
        self.logger = get_logger()
        self.request_id = 0

    def _get_next_request_id(self) -> int:
        """Get next request ID."""
        self.request_id += 1
        return self.request_id

    def call_server(
        self,
        server_name: str,
        method: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call an MCP server method.

        Args:
            server_name: Server name (email_server, linkedin_server)
            method: Method name (send_email, create_post, etc.)
            params: Method parameters

        Returns:
            Result dictionary from server

        Raises:
            ValueError: If server not found or method fails
        """
        request_id = self._get_next_request_id()

        # Log the call
        self.logger.info(
            component="mcp",
            action="client_call",
            actor="mcp_client",
            target=f"{server_name}.{method}",
            details={
                "request_id": request_id,
                "params": params,
                "dry_run": self.dry_run
            }
        )

        # In DRY_RUN mode, simulate the call
        if self.dry_run:
            return self._simulate_call(server_name, method, params, request_id)

        # In production, would make actual HTTP/RPC call to server
        # For now, import and call server directly
        try:
            if server_name == 'email_server':
                from mcp_servers.email_server import EmailMCPServer
                server = EmailMCPServer()
            elif server_name == 'linkedin_server':
                from mcp_servers.linkedin_server import LinkedInMCPServer
                server = LinkedInMCPServer()
            else:
                raise ValueError(f"Unknown server: {server_name}")

            # Call the server
            result = server.handle_request(method, params, request_id)

            self.logger.info(
                component="mcp",
                action="client_call_success",
                actor="mcp_client",
                target=f"{server_name}.{method}",
                details={
                    "request_id": request_id,
                    "result": result
                }
            )

            return result

        except Exception as e:
            self.logger.error(
                component="mcp",
                action="client_call_failed",
                actor="mcp_client",
                target=f"{server_name}.{method}",
                details={
                    "request_id": request_id,
                    "error": str(e)
                }
            )
            raise

    def _simulate_call(
        self,
        server_name: str,
        method: str,
        params: Dict[str, Any],
        request_id: int
    ) -> Dict[str, Any]:
        """
        Simulate an MCP call in DRY_RUN mode.

        Args:
            server_name: Server name
            method: Method name
            params: Method parameters
            request_id: Request ID

        Returns:
            Simulated result
        """
        self.logger.info(
            component="mcp",
            action="simulated_call",
            actor="mcp_client",
            target=f"{server_name}.{method}",
            details={
                "request_id": request_id,
                "params": params,
                "note": "DRY_RUN mode - no actual execution"
            }
        )

        # Return simulated results based on method
        if method == 'send_email':
            return {
                'status': 'sent',
                'message_id': f'simulated_msg_{request_id}',
                'to': params.get('to', 'unknown'),
                'subject': params.get('subject', 'unknown'),
                'simulated': True
            }
        elif method == 'create_post':
            return {
                'status': 'published',
                'post_id': f'simulated_post_{request_id}',
                'content': params.get('content', '')[:100],
                'visibility': params.get('visibility', 'public'),
                'simulated': True
            }
        elif method == 'get_status':
            return {
                'status': 'delivered',
                'message_id': params.get('message_id', 'unknown'),
                'simulated': True
            }
        elif method == 'get_post_stats':
            return {
                'post_id': params.get('post_id', 'unknown'),
                'status': 'published',
                'stats': {
                    'views': 0,
                    'likes': 0,
                    'comments': 0,
                    'shares': 0
                },
                'simulated': True
            }
        else:
            return {
                'status': 'success',
                'simulated': True
            }

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_name: Optional[str] = None,
        cc: Optional[list] = None,
        bcc: Optional[list] = None,
        html: bool = False
    ) -> Dict[str, Any]:
        """
        Send an email via Email MCP server.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            from_name: Sender name (optional)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            html: Whether body is HTML (optional)

        Returns:
            Result with message_id and status
        """
        params = {
            'to': to,
            'subject': subject,
            'body': body
        }

        if from_name:
            params['from_name'] = from_name
        if cc:
            params['cc'] = cc
        if bcc:
            params['bcc'] = bcc
        if html:
            params['html'] = html

        return self.call_server('email_server', 'send_email', params)

    def create_linkedin_post(
        self,
        content: str,
        hashtags: Optional[list] = None,
        visibility: str = 'public'
    ) -> Dict[str, Any]:
        """
        Create a LinkedIn post via LinkedIn MCP server.

        Args:
            content: Post content text
            hashtags: List of hashtags (optional)
            visibility: Post visibility (public, connections)

        Returns:
            Result with post_id and status
        """
        params = {
            'content': content,
            'visibility': visibility
        }

        if hashtags:
            params['hashtags'] = hashtags

        return self.call_server('linkedin_server', 'create_post', params)

    def get_email_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get email send status.

        Args:
            message_id: Gmail message ID

        Returns:
            Status information
        """
        return self.call_server('email_server', 'get_status', {'message_id': message_id})

    def get_linkedin_post_stats(self, post_id: str) -> Dict[str, Any]:
        """
        Get LinkedIn post statistics.

        Args:
            post_id: Post identifier

        Returns:
            Post statistics
        """
        return self.call_server('linkedin_server', 'get_post_stats', {'post_id': post_id})

    def validate_email_address(self, email: str) -> Dict[str, Any]:
        """
        Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            Validation result
        """
        return self.call_server('email_server', 'validate_address', {'email': email})


# Global instance
_mcp_client = None


def get_mcp_client() -> MCPClient:
    """Get or create the global MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client
