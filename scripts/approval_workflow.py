"""
ApprovalWorkflow class - Manages human-in-the-loop approval workflow.
Handles approval request creation, status checking, and timeout management.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from scripts.logger import get_logger
from scripts.file_utils import atomic_write


class ApprovalWorkflow:
    """
    File-based approval workflow for sensitive actions.

    Approval flow:
    1. Create approval request in Pending_Approval/
    2. Wait for human to move file to Approved/ or Rejected/
    3. Execute action if approved, cancel if rejected
    4. Auto-reject if timeout expires
    """

    def __init__(self, timeout_hours: int = 24):
        """
        Initialize approval workflow.

        Args:
            timeout_hours: Hours before approval request expires (default: 24)
        """
        self.timeout_hours = timeout_hours
        self.pending_dir = Path('AI_Employee_Vault/Pending_Approval')
        self.approved_dir = Path('AI_Employee_Vault/Approved')
        self.rejected_dir = Path('AI_Employee_Vault/Rejected')
        self.logger = get_logger()

        # Ensure directories exist
        for directory in [self.pending_dir, self.approved_dir, self.rejected_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def request_approval(
        self,
        action_id: str,
        action_type: str,
        description: str,
        risk_level: str,
        action_data: Dict[str, Any],
        plan_id: Optional[str] = None
    ) -> Path:
        """
        Create approval request file.

        Args:
            action_id: Unique action identifier
            action_type: Type of action (email_send, linkedin_post, payment, etc.)
            description: Human-readable description of the action
            risk_level: Risk level (low, medium, high)
            action_data: Action-specific data dictionary
            plan_id: Related plan ID (optional)

        Returns:
            Path to created approval request file
        """
        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=self.timeout_hours)

        # Build approval request content
        content = f"""# Approval Request: {action_type}

**Action ID**: {action_id}
**Risk Level**: {risk_level}
**Created**: {created_at.isoformat()}Z
**Expires**: {expires_at.isoformat()}Z
**Related Plan**: {plan_id or 'None'}

## Description

{description}

## Risk Assessment

- **Risk Level**: {risk_level}
- **Action Type**: {action_type}
- **Requires Approval**: Yes

## Action Details

{self._format_action_details(action_data)}

## Instructions

To approve this action:
1. Review the description and risk assessment above
2. Move this file to: `AI_Employee_Vault/Approved/`
3. The system will execute the action automatically

To reject this action:
1. Move this file to: `AI_Employee_Vault/Rejected/`
2. The system will cancel the action

**Timeout**: This request will expire in {self.timeout_hours} hours if not approved.

## Metadata

```json
{json.dumps({
    "action_id": action_id,
    "action_type": action_type,
    "risk_level": risk_level,
    "created_at": created_at.isoformat() + 'Z',
    "expires_at": expires_at.isoformat() + 'Z',
    "plan_id": plan_id,
    "action_data": action_data
}, indent=2)}
```
"""

        # Write approval request file
        approval_file = self.pending_dir / f"{action_id}.md"
        atomic_write(str(approval_file), content)

        # Log approval request
        self.logger.info(
            component="approval",
            action="approval_requested",
            actor="approval_workflow",
            target=action_id,
            details={
                "action_type": action_type,
                "risk_level": risk_level,
                "expires_at": expires_at.isoformat() + 'Z'
            }
        )

        return approval_file

    def _format_action_details(self, action_data: Dict[str, Any]) -> str:
        """
        Format action data for display in approval request.

        Args:
            action_data: Action data dictionary

        Returns:
            Formatted string
        """
        lines = []
        for key, value in action_data.items():
            # Format key as title case with spaces
            formatted_key = key.replace('_', ' ').title()
            lines.append(f"- **{formatted_key}**: {value}")

        return '\n'.join(lines) if lines else "No additional details"

    def check_approval_status(self, action_id: str) -> Tuple[str, Optional[Path]]:
        """
        Check approval status for an action.

        Args:
            action_id: Action ID

        Returns:
            Tuple of (status, file_path)
            status: 'approved', 'rejected', 'pending', 'timeout', or 'not_found'
            file_path: Path to approval file (if found)
        """
        # Check if approved
        approved_file = self.approved_dir / f"{action_id}.md"
        if approved_file.exists():
            self.logger.info(
                component="approval",
                action="approval_granted",
                actor="human",
                target=action_id,
                details={"status": "approved"}
            )
            return 'approved', approved_file

        # Check if rejected
        rejected_file = self.rejected_dir / f"{action_id}.md"
        if rejected_file.exists():
            self.logger.info(
                component="approval",
                action="approval_rejected",
                actor="human",
                target=action_id,
                details={"status": "rejected"}
            )
            return 'rejected', rejected_file

        # Check if still pending
        pending_file = self.pending_dir / f"{action_id}.md"
        if pending_file.exists():
            # Check for timeout
            if self._is_expired(pending_file):
                # Move to rejected due to timeout
                pending_file.rename(rejected_file)

                self.logger.warning(
                    component="approval",
                    action="approval_timeout",
                    actor="system",
                    target=action_id,
                    details={"status": "timeout", "timeout_hours": self.timeout_hours}
                )

                return 'timeout', rejected_file

            return 'pending', pending_file

        # Not found
        return 'not_found', None

    def _is_expired(self, approval_file: Path) -> bool:
        """
        Check if approval request has expired.

        Args:
            approval_file: Path to approval file

        Returns:
            True if expired, False otherwise
        """
        # Read metadata from file
        try:
            with open(approval_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract expires_at from metadata JSON
            if '```json' in content:
                json_start = content.index('```json') + 7
                json_end = content.index('```', json_start)
                metadata = json.loads(content[json_start:json_end])

                expires_at_str = metadata.get('expires_at', '')
                if expires_at_str:
                    expires_at = datetime.fromisoformat(expires_at_str.replace('Z', ''))
                    return datetime.now() > expires_at

        except Exception:
            pass

        # Fallback: check file modification time
        file_age_hours = (time.time() - approval_file.stat().st_mtime) / 3600
        return file_age_hours > self.timeout_hours

    def wait_for_approval(
        self,
        action_id: str,
        poll_interval: int = 60,
        max_wait_seconds: Optional[int] = None
    ) -> str:
        """
        Wait for approval decision (blocking).

        Args:
            action_id: Action ID
            poll_interval: Seconds between status checks (default: 60)
            max_wait_seconds: Maximum wait time in seconds (None = wait until timeout)

        Returns:
            Final status: 'approved', 'rejected', or 'timeout'
        """
        start_time = time.time()

        while True:
            status, _ = self.check_approval_status(action_id)

            if status in ['approved', 'rejected', 'timeout', 'not_found']:
                return status

            # Check max wait time
            if max_wait_seconds and (time.time() - start_time) > max_wait_seconds:
                return 'pending'

            # Wait before next check
            time.sleep(poll_interval)

    def get_pending_approvals(self) -> list[Dict[str, Any]]:
        """
        Get list of all pending approval requests.

        Returns:
            List of approval request metadata dictionaries
        """
        pending = []

        for approval_file in self.pending_dir.glob('*.md'):
            try:
                with open(approval_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract metadata
                if '```json' in content:
                    json_start = content.index('```json') + 7
                    json_end = content.index('```', json_start)
                    metadata = json.loads(content[json_start:json_end])
                    pending.append(metadata)

            except Exception:
                continue

        return pending


# Global workflow instance
_workflow = None


def get_approval_workflow() -> ApprovalWorkflow:
    """Get or create the global approval workflow instance."""
    global _workflow
    if _workflow is None:
        import os
        timeout_hours = int(os.getenv('APPROVAL_TIMEOUT_HOURS', '24'))
        _workflow = ApprovalWorkflow(timeout_hours=timeout_hours)
    return _workflow
