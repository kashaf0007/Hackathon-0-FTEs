"""Approval Request model for Bronze Tier Constitutional FTE."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional


class ApprovalRequest(BaseModel):
    """Approval request for high-risk actions.

    Represents a high-risk action awaiting human approval.
    Blocks execution until manually approved or rejected.
    """

    request_id: str = Field(..., description="Unique request identifier (e.g., approval-001)")
    task_id: str = Field(..., description="Associated task ID")
    action: str = Field(..., description="Action requiring approval")
    risk_level: Literal["MEDIUM", "HIGH"] = Field(..., description="Risk classification (LOW doesn't require approval)")
    justification: str = Field(..., description="Why this action is needed")
    impact: str = Field(..., description="What will happen if approved")
    created: datetime = Field(default_factory=datetime.now, description="Request creation timestamp")
    status: Literal["PENDING", "APPROVED", "REJECTED"] = Field(
        default="PENDING",
        description="Current approval status"
    )
    approver: Optional[str] = Field(None, description="Who approved/rejected")
    decision_time: Optional[datetime] = Field(None, description="When decision was made")
    notes: Optional[str] = Field(None, description="Approver notes")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def is_stale(self, days: int = 7) -> bool:
        """Check if approval request is stale (older than specified days)."""
        age = datetime.now() - self.created
        return age.days > days and self.status == "PENDING"

    def approve(self, approver: str, notes: Optional[str] = None) -> None:
        """Approve the request."""
        self.status = "APPROVED"
        self.approver = approver
        self.decision_time = datetime.now()
        self.notes = notes

    def reject(self, approver: str, notes: Optional[str] = None) -> None:
        """Reject the request."""
        self.status = "REJECTED"
        self.approver = approver
        self.decision_time = datetime.now()
        self.notes = notes
