"""Approval Guard skill for Bronze Tier Constitutional FTE.

Enforces Autonomy Levels & Permission Boundaries.
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from src.skills.base import BaseSkill
from src.models import Task, ApprovalRequest
from src.utils import atomic_write, format_markdown_approval


class ApprovalGuardSkill(BaseSkill):
    """Approval Guard skill implementation.

    Evaluates action risk and enforces permission boundaries.
    Creates approval requests for high-risk actions and blocks execution.
    """

    # High-risk action types that require approval
    HIGH_RISK_ACTIONS = {
        "delete_file",
        "send_email",
        "payment",
        "execute_payment",
        "post_social_media",
        "dm_reply",
        "bulk_operation"
    }

    # Medium-risk action types
    MEDIUM_RISK_ACTIONS = {
        "move_file_outside_vault",
        "modify_config",
        "create_external_resource"
    }

    def __init__(self, skill_path: Path, pending_approval_path: Path):
        """Initialize approval guard skill.

        Args:
            skill_path: Path to skill directory
            pending_approval_path: Path to pending approval directory
        """
        super().__init__(skill_path)
        self.pending_approval_path = Path(pending_approval_path)
        self.pending_approval_path.mkdir(parents=True, exist_ok=True)

    def execute(self, task: Task, dry_run: bool = False) -> Dict[str, Any]:
        """Execute approval guard (not typically called directly).

        Args:
            task: Task to execute
            dry_run: If True, simulate execution

        Returns:
            Execution results
        """
        return {
            "success": True,
            "output": "Approval Guard is used via evaluate_risk() method, not execute()",
            "error": None
        }

    def can_handle(self, task: Task) -> bool:
        """Check if skill can handle task.

        Approval Guard doesn't handle tasks directly.

        Args:
            task: Task to check

        Returns:
            False (approval guard is a utility, not a task handler)
        """
        return False

    def get_risk_level(self, task: Task) -> str:
        """Get risk level for task.

        Args:
            task: Task to evaluate

        Returns:
            Risk level: LOW, MEDIUM, or HIGH
        """
        task_type = task.type.lower()

        if task_type in self.HIGH_RISK_ACTIONS:
            return "HIGH"
        elif task_type in self.MEDIUM_RISK_ACTIONS:
            return "MEDIUM"
        else:
            return "LOW"

    def evaluate_risk(self, task: Task) -> str:
        """Evaluate risk level for a task.

        Args:
            task: Task to evaluate

        Returns:
            Risk level: LOW, MEDIUM, or HIGH
        """
        return self.get_risk_level(task)

    def requires_approval(self, task: Task) -> bool:
        """Check if task requires approval.

        Args:
            task: Task to check

        Returns:
            True if task requires approval (MEDIUM or HIGH risk)
        """
        risk = self.evaluate_risk(task)
        return risk in ["MEDIUM", "HIGH"]

    def create_approval_request(
        self,
        task: Task,
        justification: str,
        impact: str,
        dry_run: bool = False
    ) -> ApprovalRequest:
        """Create approval request for high-risk task.

        Args:
            task: Task requiring approval
            justification: Why this action is needed
            impact: What will happen if approved
            dry_run: If True, simulate creation

        Returns:
            Created approval request

        Raises:
            IOError: If approval file creation fails
            PermissionError: If no write permission to pending_approval_path
        """
        risk_level = self.evaluate_risk(task)

        # Generate request ID
        existing_requests = list(self.pending_approval_path.glob("approval-*.md"))
        request_num = len(existing_requests) + 1
        request_id = f"approval-{request_num:03d}"

        # Create approval request model
        approval = ApprovalRequest(
            request_id=request_id,
            task_id=task.task_id,
            action=task.type,
            risk_level=risk_level,
            justification=justification,
            impact=impact
        )

        # Write approval request file
        if not dry_run:
            try:
                # Ensure directory exists and is writable
                self.pending_approval_path.mkdir(parents=True, exist_ok=True)

                import os
                if not os.access(self.pending_approval_path, os.W_OK):
                    raise PermissionError(f"No write permission for {self.pending_approval_path}")

                approval_file = self.pending_approval_path / f"{request_id}.md"
                content = format_markdown_approval(
                    request_id=approval.request_id,
                    task_id=approval.task_id,
                    created=approval.created.isoformat(),
                    risk_level=approval.risk_level,
                    action=approval.action,
                    justification=approval.justification,
                    impact=approval.impact,
                    status=approval.status
                )
                atomic_write(approval_file, content)
            except PermissionError as e:
                raise PermissionError(f"Failed to create approval request: {str(e)}")
            except Exception as e:
                raise IOError(f"Failed to write approval request file: {str(e)}")

        return approval

    def check_approval_status(self, task: Task) -> str:
        """Check if task has been approved.

        Args:
            task: Task to check

        Returns:
            Approval status: PENDING, APPROVED, or REJECTED
        """
        # Find approval request for this task
        for approval_file in self.pending_approval_path.glob("*.md"):
            content = approval_file.read_text(encoding='utf-8')
            if f"**Task ID**: {task.task_id}" in content:
                # Parse status from file
                if "**Status**: APPROVED" in content:
                    return "APPROVED"
                elif "**Status**: REJECTED" in content:
                    return "REJECTED"
                else:
                    return "PENDING"

        return "PENDING"
