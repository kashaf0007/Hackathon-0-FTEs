"""Logging & Audit skill for Bronze Tier Constitutional FTE.

Guarantees Transparency principle by logging all actions.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from src.skills.base import BaseSkill
from src.models import Task, LogEntry
from src.utils import atomic_write


class LoggingAuditSkill(BaseSkill):
    """Logging & Audit skill implementation.

    Records every action to daily log files for complete transparency.
    Flags constitutional violations and maintains audit trail.
    """

    def __init__(self, skill_path: Path, logs_path: Path):
        """Initialize logging skill.

        Args:
            skill_path: Path to skill directory
            logs_path: Path to logs directory (AI_Employee_Vault/Logs/)
        """
        super().__init__(skill_path)
        self.logs_path = Path(logs_path)
        self.logs_path.mkdir(parents=True, exist_ok=True)

    def execute(self, task: Task, dry_run: bool = False) -> Dict[str, Any]:
        """Execute logging (not typically called directly).

        Args:
            task: Task to execute
            dry_run: If True, simulate execution

        Returns:
            Execution results
        """
        return {
            "success": True,
            "output": "Logging skill is used via log() method, not execute()",
            "error": None
        }

    def can_handle(self, task: Task) -> bool:
        """Check if skill can handle task.

        Logging skill doesn't handle tasks directly.

        Args:
            task: Task to check

        Returns:
            False (logging is a utility, not a task handler)
        """
        return False

    def log(self, entry: LogEntry) -> None:
        """Log an entry to today's log file.

        Args:
            entry: Log entry to record

        Raises:
            IOError: If log write fails
        """
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs_path / f"{today}.json"

        # Read existing entries
        entries = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    entries = json.load(f)
            except json.JSONDecodeError:
                # If file is corrupted, start fresh
                entries = []

        # Append new entry
        entries.append(entry.model_dump(mode='json'))

        # Write atomically
        atomic_write(log_file, json.dumps(entries, indent=2))

    def log_action(
        self,
        action: str,
        risk_level: str,
        outcome: str,
        task_id: str = None,
        skill_used: str = None,
        approval_status: str = "AUTO_APPROVED",
        error: str = None,
        constitutional_compliance: bool = True,
        dry_run: bool = False,
        **metadata
    ) -> None:
        """Log an action with all required metadata.

        Args:
            action: Action performed
            risk_level: LOW, MEDIUM, or HIGH
            outcome: SUCCESS, FAILURE, or BLOCKED
            task_id: Associated task ID
            skill_used: Skill that performed action
            approval_status: AUTO_APPROVED, PENDING_APPROVAL, APPROVED, or REJECTED
            error: Error message if failed
            constitutional_compliance: Whether action complies with constitution
            dry_run: Whether this was a simulated action
            **metadata: Additional context (duration_ms, retry_count, etc.)
        """
        entry = LogEntry(
            action=action,
            task_id=task_id,
            skill_used=skill_used,
            risk_level=risk_level,
            approval_status=approval_status,
            outcome=outcome,
            error=error,
            constitutional_compliance=constitutional_compliance,
            dry_run=dry_run,
            metadata=metadata
        )
        self.log(entry)

    def get_todays_logs(self) -> List[Dict[str, Any]]:
        """Get all log entries for today.

        Returns:
            List of log entries
        """
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs_path / f"{today}.json"

        if not log_file.exists():
            return []

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def count_violations(self) -> int:
        """Count constitutional violations in today's logs.

        Returns:
            Number of violations
        """
        logs = self.get_todays_logs()
        return sum(1 for log in logs if not log.get('constitutional_compliance', True))
