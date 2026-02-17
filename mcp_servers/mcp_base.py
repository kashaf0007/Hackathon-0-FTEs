"""
MCP (Model Context Protocol) base server implementation.
Provides JSON-RPC 2.0 server functionality with DRY_RUN support.
"""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


class MCPServer(ABC):
    """
    Base class for MCP servers implementing JSON-RPC 2.0 protocol.

    Subclasses must implement the execute() method to handle specific actions.
    """

    def __init__(self, name: str, port: Optional[int] = None):
        """
        Initialize MCP server.

        Args:
            name: Server name (e.g., 'email-mcp-server')
            port: Server port (optional, for HTTP transport)
        """
        self.name = name
        self.port = port
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        self.log_dir = Path('AI_Employee_Vault/Logs')
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def handle_request(self, method: str, params: Dict[str, Any], request_id: Any = None) -> Dict[str, Any]:
        """
        Handle a JSON-RPC 2.0 request.

        Args:
            method: Method name to execute
            params: Method parameters
            request_id: Request ID for response correlation

        Returns:
            JSON-RPC 2.0 response dictionary
        """
        try:
            # Log request
            self._log_request(method, params)

            # Check if in DRY_RUN mode
            if self.dry_run:
                result = self._simulate_action(method, params)
                self._log_response(method, result, simulated=True)
                return self._create_response(result, request_id)

            # Execute actual action
            result = self.execute(method, params)
            self._log_response(method, result, simulated=False)
            return self._create_response(result, request_id)

        except Exception as e:
            error = self._create_error(-32603, f"Internal error: {str(e)}", request_id)
            self._log_error(method, str(e))
            return error

    @abstractmethod
    def execute(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the actual action (must be implemented by subclasses).

        Args:
            method: Method name
            params: Method parameters

        Returns:
            Result dictionary

        Raises:
            NotImplementedError: If method is not supported
            Exception: If execution fails
        """
        raise NotImplementedError("Subclasses must implement execute()")

    def _simulate_action(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate action in DRY_RUN mode.

        Args:
            method: Method name
            params: Method parameters

        Returns:
            Simulated result dictionary
        """
        return {
            "status": "simulated",
            "method": method,
            "timestamp": datetime.now().isoformat() + "Z",
            "message": f"DRY_RUN: Would execute {method} with params: {json.dumps(params, indent=2)}"
        }

    def _create_response(self, result: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """Create JSON-RPC 2.0 success response."""
        response = {
            "jsonrpc": "2.0",
            "result": result
        }
        if request_id is not None:
            response["id"] = request_id
        return response

    def _create_error(self, code: int, message: str, request_id: Any, data: Any = None) -> Dict[str, Any]:
        """Create JSON-RPC 2.0 error response."""
        error = {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            }
        }
        if data is not None:
            error["error"]["data"] = data
        if request_id is not None:
            error["id"] = request_id
        return error

    def _log_request(self, method: str, params: Dict[str, Any]) -> None:
        """Log MCP request."""
        log_entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "info",
            "component": "mcp",
            "action": "request",
            "actor": self.name,
            "target": method,
            "status": "pending",
            "details": {
                "method": method,
                "params": params,
                "dry_run": self.dry_run
            }
        }
        self._write_log(log_entry)

    def _log_response(self, method: str, result: Dict[str, Any], simulated: bool) -> None:
        """Log MCP response."""
        log_entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "info",
            "component": "mcp",
            "action": "response",
            "actor": self.name,
            "target": method,
            "status": "simulated" if simulated else "success",
            "details": {
                "method": method,
                "result": result,
                "dry_run": self.dry_run
            }
        }
        self._write_log(log_entry)

    def _log_error(self, method: str, error: str) -> None:
        """Log MCP error."""
        log_entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "error",
            "component": "mcp",
            "action": "error",
            "actor": self.name,
            "target": method,
            "status": "failure",
            "details": {
                "method": method,
                "error": error,
                "dry_run": self.dry_run
            }
        }
        self._write_log(log_entry)

    def _write_log(self, entry: Dict[str, Any]) -> None:
        """Write log entry to daily log file."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"{today}.json"

        # Read existing log
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                log_data = {"date": today, "entries": []}
        else:
            log_data = {"date": today, "entries": []}

        # Append entry
        log_data["entries"].append(entry)

        # Write atomically
        temp_file = log_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        temp_file.replace(log_file)

    def get_server_info(self) -> Dict[str, Any]:
        """Get server information."""
        return {
            "name": self.name,
            "version": "1.0.0",
            "protocol": "json-rpc-2.0",
            "dry_run": self.dry_run,
            "port": self.port
        }
