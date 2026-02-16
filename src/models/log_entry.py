"""Log Entry model for Bronze Tier Constitutional FTE."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional, Dict, Any


class LogEntry(BaseModel):
    """Log entry for audit trail.

    Records every action taken by the system for transparency and accountability.
    All actions must be logged with complete metadata.
    """

    timestamp: datetime = Field(default_factory=datetime.now, description="Action timestamp (UTC)")
    task_id: Optional[str] = Field(None, description="Associated task ID")
    action: str = Field(..., description="Action performed")
    skill_used: Optional[str] = Field(None, description="Skill that performed action")
    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(..., description="Risk classification of action")
    approval_status: Literal["AUTO_APPROVED", "PENDING_APPROVAL", "APPROVED", "REJECTED"] = Field(
        ...,
        description="Approval status of action"
    )
    outcome: Literal["SUCCESS", "FAILURE", "BLOCKED"] = Field(..., description="Result of action")
    error: Optional[str] = Field(None, description="Error message if failed")
    constitutional_compliance: bool = Field(
        default=True,
        description="Whether action complies with constitution"
    )
    dry_run: bool = Field(default=False, description="Whether this was a simulated action")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @classmethod
    def create_success(
        cls,
        action: str,
        risk_level: Literal["LOW", "MEDIUM", "HIGH"],
        task_id: Optional[str] = None,
        skill_used: Optional[str] = None,
        dry_run: bool = False,
        **metadata
    ) -> "LogEntry":
        """Create a success log entry."""
        return cls(
            action=action,
            task_id=task_id,
            skill_used=skill_used,
            risk_level=risk_level,
            approval_status="AUTO_APPROVED",
            outcome="SUCCESS",
            dry_run=dry_run,
            metadata=metadata
        )

    @classmethod
    def create_failure(
        cls,
        action: str,
        error: str,
        risk_level: Literal["LOW", "MEDIUM", "HIGH"],
        task_id: Optional[str] = None,
        skill_used: Optional[str] = None,
        dry_run: bool = False,
        **metadata
    ) -> "LogEntry":
        """Create a failure log entry."""
        return cls(
            action=action,
            task_id=task_id,
            skill_used=skill_used,
            risk_level=risk_level,
            approval_status="AUTO_APPROVED",
            outcome="FAILURE",
            error=error,
            dry_run=dry_run,
            metadata=metadata
        )

    @classmethod
    def create_blocked(
        cls,
        action: str,
        risk_level: Literal["MEDIUM", "HIGH"],
        task_id: Optional[str] = None,
        skill_used: Optional[str] = None,
        dry_run: bool = False,
        **metadata
    ) -> "LogEntry":
        """Create a blocked log entry for high-risk actions."""
        return cls(
            action=action,
            task_id=task_id,
            skill_used=skill_used,
            risk_level=risk_level,
            approval_status="PENDING_APPROVAL",
            outcome="BLOCKED",
            dry_run=dry_run,
            metadata=metadata
        )
