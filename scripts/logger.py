"""
Logger module for AI Employee system.
Provides JSON-formatted logging with timestamp and structured data.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class Logger:
    """
    JSON-based logger for AI Employee operations.
    Logs are written to daily files in AI_Employee_Vault/Logs/
    """

    def __init__(self, log_dir: str = "AI_Employee_Vault/Logs"):
        """
        Initialize logger with log directory.

        Args:
            log_dir: Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _get_log_file(self) -> Path:
        """Get the log file path for today."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"{today}.json"

    def _read_log_file(self, log_file: Path) -> Dict[str, Any]:
        """Read existing log file or return empty structure."""
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, start fresh
                return {"date": datetime.now().strftime("%Y-%m-%d"), "entries": []}
        return {"date": datetime.now().strftime("%Y-%m-%d"), "entries": []}

    def _write_log_file(self, log_file: Path, data: Dict[str, Any]) -> None:
        """Write log data to file atomically."""
        # Write to temp file first, then rename (atomic operation)
        temp_file = log_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_file.replace(log_file)

    def log(
        self,
        level: str,
        component: str,
        action: str,
        actor: str,
        target: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None
    ) -> None:
        """
        Log an event with structured data.

        Args:
            level: Log level (info, warning, error)
            component: Component name (watcher, skill, mcp, orchestrator)
            action: Action type (event_detected, task_executed, etc.)
            actor: Who/what performed the action
            target: What was acted upon
            status: Action status (success, failure, pending)
            details: Additional details dictionary
            duration_ms: Action duration in milliseconds
        """
        log_file = self._get_log_file()
        log_data = self._read_log_file(log_file)

        entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": level,
            "component": component,
            "action": action,
            "actor": actor,
            "target": target,
            "status": status,
            "details": details or {},
        }

        if duration_ms is not None:
            entry["duration_ms"] = duration_ms

        log_data["entries"].append(entry)
        self._write_log_file(log_file, log_data)

    def info(self, component: str, action: str, actor: str, target: str, **kwargs) -> None:
        """Log an info-level event."""
        self.log("info", component, action, actor, target, "success", **kwargs)

    def warning(self, component: str, action: str, actor: str, target: str, **kwargs) -> None:
        """Log a warning-level event."""
        self.log("warning", component, action, actor, target, "pending", **kwargs)

    def error(self, component: str, action: str, actor: str, target: str, **kwargs) -> None:
        """Log an error-level event."""
        self.log("error", component, action, actor, target, "failure", **kwargs)


# Global logger instance
_logger = None


def get_logger() -> Logger:
    """Get or create the global logger instance."""
    global _logger
    if _logger is None:
        _logger = Logger()
    return _logger
